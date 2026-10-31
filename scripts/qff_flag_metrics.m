%% ====================================================================
%  Q feed-forward - quantitative metrics of the maneuver flag
%
%  Reference flag: the SAME hysteresis (jOn / jOff) applied to the jerk of
%  the ground truth (zero-phase Butterworth, offline). It marks when the
%  maneuver "should" be detected.
%  Estimated flag: the hysteresis applied to the jerk estimated online by
%  the auxiliary filter. Since the auxiliary filter does not depend on the
%  flag (feed-forward), the flag can be recomputed offline for any
%  threshold from the logged jerk: the sensitivity on jOn needs no rerun.
%
%  Metrics
%   - activation delay : t_on(estimated) - t_on(reference), matched within
%                        [-tolPre, +tolPost] around each reference onset
%                        (median and IQR over the maneuvers, + = late)
%   - missed           : reference maneuvers with no estimated activation
%   - spurious         : estimated activations that do not overlap any
%                        reference maneuver (count and per minute)
%   - false-active time: fraction of the time outside the maneuvers in
%                        which the estimated flag is active
%   - active time      : fraction of time with the estimated flag active
%   - RMSE v_x, a_x    : global and local (inside the reference maneuvers)
% ====================================================================

%% ==================== INPUTS (fill in) ====================
% jerk estimated online by the auxiliary filter (as plotted in Fig. jerk)
% tJ   = ...;   jEst = ...;
% ground truth: time, longitudinal speed and acceleration
% tGt  = double(gt.stamp(:)) - t0;   vGt = double(gt.vx(:));   aGt = double(gt.ax(:));
% estimates to compare in the RMSE table (one struct per log)
% est(1) = struct('name','CCA-baseline',     't',..., 'v',..., 'a',...);
% est(2) = struct('name','CCA - Q = 500',    't',..., 'v',..., 'a',...);
% est(3) = struct('name','CCA-feed-forward', 't',..., 'v',..., 'a',...);

%% ==================== PARAMETERS ====================
jOn      = 15;                 % m/s^3, activation threshold
jOff     = 5;                  % m/s^3, deactivation threshold
jOnList  = [10 15 20 25 30];   % sensitivity on jOn (jOff kept fixed)
fcGt     = 5;                  % Hz, Butterworth cutoff for the GT jerk
dtG      = 0.01;               % s, uniform analysis grid
tolPre   = 0.20;               % s, an estimated onset may precede the reference by this much
tolPost  = 1.50;               % s, ...or follow it by at most this much
minDur   = 0.10;               % s, minimum duration of a reference maneuver
TIME_WINDOW = [500 1400];      % s, [] = whole log

%% ==================== COMMON GRID ====================
t0g = max(tJ(1), tGt(1));  t1g = min(tJ(end), tGt(end));
if ~isempty(TIME_WINDOW)
    t0g = max(t0g, TIME_WINDOW(1));  t1g = min(t1g, TIME_WINDOW(2));
end
t  = (t0g:dtG:t1g).';
[tGu, iu] = unique(tGt);
aG = interp1(tGu, aGt(iu), t, 'linear');
[b, a] = butter(2, fcGt / (0.5/dtG));
jG = filtfilt(b, a, gradient(filtfilt(b, a, aG), dtG));     % GT jerk, zero phase
[tJu, ij] = unique(tJ);
jE = interp1(tJu, jEst(ij), t, 'previous', 0);              % held between updates

%% ==================== REFERENCE MANEUVERS ====================
fG = hyst(abs(jG), jOn, jOff);
evG = edges(t, fG);
evG = evG(evG(:,2) - evG(:,1) >= minDur, :);
fGx = false(size(t));                                       % reference mask, extended
for m = 1:size(evG,1)
    fGx(t >= evG(m,1) - tolPre & t <= evG(m,2) + tolPost) = true;
end
fGin = false(size(t));                                      % reference mask, strict (local RMSE)
for m = 1:size(evG,1)
    fGin(t >= evG(m,1) & t <= evG(m,2)) = true;
end

%% ==================== FLAG METRICS (nominal thresholds) ====================
S = flagMetrics(t, jE, jOn, jOff, evG, fGx, tolPre, tolPost);
Tmin = (t(end) - t(1)) / 60;
fprintf('\n=== Maneuver flag, jOn = %g, jOff = %g m/s^3 ===\n', jOn, jOff);
fprintf(' reference maneuvers        : %d\n', size(evG,1));
fprintf(' detected / missed          : %d / %d\n', S.nDet, S.nMiss);
fprintf(' activation delay [ms]      : median %+.0f  IQR [%+.0f %+.0f]\n', ...
        1e3*S.dMed, 1e3*S.dQ(1), 1e3*S.dQ(2));
fprintf(' spurious activations       : %d  (%.2f per minute)\n', S.nSpur, S.nSpur/Tmin);
fprintf(' false-active time          : %.1f %% of the time outside the maneuvers\n', 100*S.fpTime);
fprintf(' flag active                : %.1f %% of the time\n', 100*S.active);

%% ==================== SENSITIVITY ON jOn ====================
fprintf('\n=== Sensitivity on jOn (jOff = %g m/s^3) ===\n', jOff);
fprintf('%8s %8s %8s %14s %10s %12s %10s\n', 'jOn', 'det', 'miss', 'delay med[ms]', ...
        'spurious', 'spur/min', 'active[%]');
SS = struct([]);
for q = 1:numel(jOnList)
    Sq = flagMetrics(t, jE, jOnList(q), min(jOff, jOnList(q)), evG, fGx, tolPre, tolPost);
    SS = [SS; Sq]; %#ok<AGROW>
    fprintf('%8g %8d %8d %+14.0f %10d %12.2f %10.1f\n', jOnList(q), Sq.nDet, Sq.nMiss, ...
            1e3*Sq.dMed, Sq.nSpur, Sq.nSpur/Tmin, 100*Sq.active);
end
figure('Color','w');
yyaxis left;  plot(jOnList, 1e3*[SS.dMed], 'o-', 'LineWidth', 1.4); ylabel('median activation delay [ms]');
yyaxis right; plot(jOnList, [SS.nSpur]/Tmin, 's-', 'LineWidth', 1.4); ylabel('spurious activations [1/min]');
xlabel('j_{on} [m/s^3]'); grid on; title('Trade-off of the activation threshold');

%% ==================== RMSE TABLE ====================
if exist('est', 'var')
    fprintf('\n=== RMSE vs GT (global / inside the maneuvers) ===\n');
    fprintf('%-20s %10s %10s %10s %10s\n', 'log', 'v glob', 'v loc', 'a glob', 'a loc');
    vG = interp1(tGu, vGt(iu), t, 'linear');
    for k = 1:numel(est)
        [te, ie] = unique(est(k).t);
        ve = interp1(te, est(k).v(ie), t, 'linear', NaN);
        ae = interp1(te, est(k).a(ie), t, 'linear', NaN);
        r  = @(e, msk) sqrt(mean(e(msk).^2, 'omitnan'));
        all = true(size(t));
        fprintf('%-20s %10.3f %10.3f %10.3f %10.3f\n', est(k).name, ...
                r(ve - vG, all), r(ve - vG, fGin), r(ae - aG, all), r(ae - aG, fGin));
    end
end

%% ==================== LOCAL FUNCTIONS ====================
function f = hyst(x, on, off)
% Hysteresis: 1 when x > on, back to 0 only when x < off.
    f = false(size(x));  s = false;
    for i = 1:numel(x)
        if ~s && x(i) > on, s = true; elseif s && x(i) < off, s = false; end
        f(i) = s;
    end
end

function ev = edges(t, f)
% [t_on t_off] of the intervals with f = 1.
    d  = diff([false; f(:); false]);
    i1 = find(d == 1);  i2 = find(d == -1) - 1;
    ev = [t(i1) t(i2)];
end

function S = flagMetrics(t, jE, on, off, evG, fGx, tolPre, tolPost)
    fE  = hyst(abs(jE), on, off);
    evE = edges(t, fE);
    nG  = size(evG,1);  d = nan(nG,1);  used = false(size(evE,1),1);
    for m = 1:nG
        k = find(evE(:,1) >= evG(m,1) - tolPre & evE(:,1) <= evG(m,1) + tolPost, 1, 'first');
        if ~isempty(k), d(m) = evE(k,1) - evG(m,1); used(k) = true; end
    end
    spur = false(size(evE,1),1);                 % activation entirely outside the maneuvers
    for k = 1:size(evE,1)
        in = t >= evE(k,1) & t <= evE(k,2);
        spur(k) = ~used(k) && ~any(fGx(in));
    end
    dd = d(isfinite(d));
    S.nDet  = numel(dd);           S.nMiss = nG - numel(dd);
    S.dMed  = median(dd);          S.dQ    = [prctile(dd,25) prctile(dd,75)];
    S.nSpur = nnz(spur);
    S.fpTime = nnz(fE & ~fGx) / max(1, nnz(~fGx));
    S.active = mean(fE);
end
