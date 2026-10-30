"""Bode diagram of the jerk differentiators H1 (dirty derivative) and H2 (Butterworth)."""
import numpy as np
import matplotlib.pyplot as plt

fc = 2.5                      # cutoff frequency [Hz]
tau = 1 / (2 * np.pi * fc)    # time constant of the dirty derivative [s]
wc = 2 * np.pi * fc           # cutoff frequency [rad/s]

f = np.logspace(-2, 2, 2000)  # [Hz]
s = 1j * 2 * np.pi * f
H0 = s                                        # ideal differentiator
H1 = s / (1 + tau * s)                        # dirty derivative
H2 = s * wc**2 / (s**2 + np.sqrt(2) * wc * s + wc**2)   # Butterworth 2nd order

db = lambda H: 20 * np.log10(np.abs(H))
ph = lambda H: np.degrees(np.unwrap(np.angle(H)))

plt.rcParams.update({"font.size": 9, "font.family": "serif"})
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.3, 4.6), sharex=True)
for H, lab, st, c in [(H0, "Ideal derivative", ":", "0.4"),
                      (H1, "Dirty derivative $H_1$", "-", "#D95319"),
                      (H2, "Butterworth $H_2$", "-", "#0072BD")]:
    a1.semilogx(f, db(H), st, color=c, lw=1.4, label=lab)
    a2.semilogx(f, ph(H), st, color=c, lw=1.4)
for a in (a1, a2):
    a.axvline(fc, color="k", ls="--", lw=0.8)
    a.grid(True, which="both", lw=0.3)
a1.set_ylabel("Magnitude [dB]")
a2.set_ylabel("Phase [deg]")
a2.set_xlabel("Frequency [Hz]")
a2.set_yticks([-90, -45, 0, 45, 90])
a1.legend(loc="lower right", frameon=True)
a1.set_xlim(f[0], f[-1])
fig.tight_layout()
fig.savefig("figures/ch5/jerk_filters_bode.pdf")
