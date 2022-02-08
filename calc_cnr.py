import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from sky_temperature import get_sky_temperature
from fsl_vs_phi_l import distance, fsl

orbit_height    = 600E3;
freq            = (7.25 + 7.75) * 0.5E9;

elevation_angle = np.arange(0, 91, 1)
antenna_temp = get_sky_temperature(elevation_angle)
distance = distance(elevation_angle, orbit_height)

loss    = 1.0 / (antenna_temp * fsl(distance, freq));
loss_db = 20 * np.log10(loss)

# Normalize to 0 dB
loss_db = loss_db - np.max(loss_db)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(elevation_angle, loss_db, color="dodgerblue")
ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base = 5.0))
ax.set_xlim(90, 0)

ax.grid(True, which = 'major')
# ax.grid(True, which = 'minor', axis='y')
ax.minorticks_on()

ax.set_title   ("CNR vs. Elevation angle (normalized to 0 dB)")
ax.set_xlabel  ("Elevation angle $\phi_l$ [deg]")
ax.set_ylabel  ("CNR/$N_0$")

plt.savefig ("../output/cnr_norm_vs_angle.svg")
plt.savefig ("../output/cnr_norm_vs_angle.png")

plt.tight_layout()
plt.show()