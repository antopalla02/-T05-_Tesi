# Table of Contents – Draft

## Abstract / Sommario

## 1. Introduction
- Motivation and problem statement

## 2. Experimental Setup and Methodology
- 2.1 Dallara AV-24
- 2.2 Dallara EAV-24
- 2.3 Sensors
  - 2.3.1 LiDAR
  - 2.3.2 RaDAR
  - 2.3.3 Cameras
  - 2.3.4 Localization
  - 2.3.5 Dallara AV-24 (sensor configuration)
  - 2.3.6 Dallara EAV-24 (sensor configuration)
- 2.4 Software Architecture: localization, perception, planning, control
- 2.5 Datasets
- 2.6 Ground Truth Reconstruction

## 3. Target Tracking Pipeline
- Perception output: RaDAR, LiDAR and camera detections
- State model: CCA motion model, EKF prediction step
- Data association: Mahalanobis gating, Munkres assignment, OOSM handling
- Correction step
- Track management
- Baseline performance and limitations under changing dynamic conditions

## 4. Adaptive Measurement Noise Matrix
- Theoretical formulation, estimator assumptions, closed-loop effect
- Definition of the measurement error in the relative frame
- Deterministic compensation and Gaussian fitting
- Temporal, cross-sensor and geometric correlations (PSD, ACF, LiDAR common mode)
- Bias observability
- Gauss–Markov model for debiasing
- Results

## 5. Q Feed-Forward
- Parallel filter architecture and sensitivity analysis on Q
- Jerk estimation (frequency-domain filtering)
- Activation logic with hysteresis (pseudocode)
- Results

## 6. RTS Smoother
- Formulation: EKF, fixed-lag RTS
- Sensitivity analysis on the window length
- Analysis with and without RaDAR measurements
- Results

## 7. Experimental Results

## 8. Conclusions and Future Work
- Conclusions
- Future work: camera bias estimation

## Open points
- Evaluation metrics: dedicated section or defined in each chapter
- Results: single chapter or per chapter
- Combination of Q feed-forward and smoother: where to present it
- Comparison of the Q feed-forward with multiple-model approaches (MMAE / IMM)
- Singer model
- Particle filter to assess the effect of nonlinearities
