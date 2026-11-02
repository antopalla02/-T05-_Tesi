# TODO – Thesis

## General
- [ ] Abstract (English) + keywords
- [ ] Abstract in lingua italiana + parole chiave
- [ ] Title page (`\puttitle` commented in main.tex)
- [ ] Acknowledgements
- [ ] Bibliography: enable `\bibliography{Thesis_bibliography}` and add the citations
      (Kalman 1960, Rauch–Tung–Striebel 1965, Fraser–Potter 1969, Fokin 2009, ...)
- [x] Experimental Results chapter removed: results presented at the end of each chapter

## Chapter 1 – Introduction
- [ ] Whole chapter (motivation, problem statement, contributions, outline)

## Chapter 2 – Experimental Setup
- [ ] Verify data without source: 550 hp push-to-pass, Leopard Imaging and HDR of the EAV cameras,
      history of the competitions (Monza 2023, Laguna Seca, A2RL April 2024 with four cars, Imola 2026)
- [ ] Caption Fig. 2.2 ("Imola, August 2026") vs text (first race in September 2026)

## Chapter 4 – Measurement Noise Analysis
- [x] Geometric Dependence: correlation with bearing and aspect angle (table)
- [ ] Fig. PSD/ACF: the two panels side by side are small, consider stacking or regenerating
- [x] Covariance matching: τ ≈ Δt/(1−α) added (α ≈ 0.9 at 10 Hz)
- [ ] Scripts: camera_intrinsic.py computes the slope on 40–120 m, the text uses 40–100 m;
      PointPillars and RaDAR slopes (eq. 4.5) not saved by the scripts
- [ ] Unused files: figures/ch4/gauss68_front_detrended.pdf, gauss68_rear_detrended.pdf

## Chapter 5 – Q Feed-Forward
- [ ] 5.2 Nominal Process Noise Tuning: text and figures with different values of Q
- [ ] Value of the inflation factor λ
- [ ] Which jerk filter is used in the tracker (dirty derivative or Butterworth)
- [ ] Quantitative results (RMSE of speed and acceleration, number of false activations)
- [ ] Figures (all to be produced/checked, currently TODO placeholders):
  - [ ] CCA estimate vs ground truth during maneuvers (introduction)
  - [ ] Estimate with different values of Q (nominal tuning)
  - [ ] Bode diagram of the transfer functions H1 (dirty derivative) and H2 (Butterworth)
  - [ ] Jerk estimate (dirty derivative, Butterworth) vs ground-truth jerk (SG)
  - [ ] Nominal vs feed-forward over a sequence of corners, with the active flag
  - [ ] Detail of a braking phase
- [ ] figures/ch5/*.png extracted from the slides are not used (to be replaced)

## Chapter 6 – Non-Causal Filtering
- [ ] Section 6.5 Combination with the Q Feed-Forward (formulation, implementation, results)
- [x] Table 6.1 vs Table 6.3 inconsistency resolved with the new metric tables
- [x] Figures replaced with the new ones:
  - [x] Fig. 6.1 speed with different windows, all sensors (braking, corner): replaced
  - [x] Fig. 6.2 RMSE and maneuver delay vs window length, all sensors (label corrected to "maneuver delay")
  - [x] Fig. 6.3 speed with different windows, without RaDAR (braking, corner): replaced
  - [x] Fig. 6.4 RMSE and maneuver delay vs window length, without RaDAR (label corrected to "maneuver delay")
  - [x] Fig. 6.5 RaDAR vs no RaDAR (replaced with the new figure with legend)

## Chapter 7 – Conclusions and Future Work
- [ ] Whole chapter (conclusions; future work: relative biases of camera and RaDAR,
      RTS + feed-forward Q)
