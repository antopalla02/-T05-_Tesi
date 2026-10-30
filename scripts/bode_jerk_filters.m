%% Bode diagram of the jerk differentiators H1 (dirty derivative) and H2 (Butterworth)
fc  = 2.5;               % cutoff frequency [Hz]
tau = 1/(2*pi*fc);       % time constant of the dirty derivative [s]
wc  = 2*pi*fc;           % cutoff frequency [rad/s]

s  = tf('s');
H0 = s;                                       % ideal differentiator
H1 = s/(1 + tau*s);                           % dirty derivative
H2 = s*wc^2/(s^2 + sqrt(2)*wc*s + wc^2);      % Butterworth 2nd order

opts = bodeoptions;  opts.FreqUnits = 'Hz';  opts.Grid = 'on';
opts.XLim = [1e-2 1e2];  opts.Title.String = '';
figure('Color','w');
bodeplot(H0, 'k:', H1, H2, {2*pi*1e-2, 2*pi*1e2}, opts);
legend('Ideal derivative', 'Dirty derivative H_1', 'Butterworth H_2', 'Location', 'southwest');
