import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ber_psk import search_ber_psk
from ber_qam import search_ber_qam
from fsl_vs_phi_l import distance, fsl, elevation_angle_to_earth_angle
from compare_ebno import pass_time
from sky_temperature import get_sky_temperature
from ber_psk import BER
from rx_temperature import get_rx_temperature


target_ber = 10**-5

scheme_required_gamma = dict()
scheme_required_gamma['BPSK']   = search_ber_psk(target_ber, 2, 1/100)

scheme_efficiency = dict()
scheme_efficiency['BPSK']       = 1

# Dataframe for storing schemes performance
df = pd.DataFrame(columns=['Scheme', 'Flyover time', 'Throughput'])

# System variables
orbit_height            = 600E3;
freq                    = (7.90 + 8.40) * 0.5E9;
bw                      = (8.40 - 7.90) * 1.0E9;
k_boltzmann             = -10*np.log10(1.38064852E-23)
brightness_temp_est     = 300
coding_rate             = 56 / 63 # BCH

elevation_angle         = np.arange(0, 90.2, 0.2)
distance_to_satellite   = distance(elevation_angle, orbit_height)
free_space_losses       = fsl(distance_to_satellite, freq)

base_station_eirp       = 6 + 6.9    # 6 dBw + 47 dBi
coding_gain             = 2
terminal_antenna_gain   = 47

additional_losses       = 1.5 + 4

# gains       = 0 + 7 + 47 + k_boltzmann 
gains       = base_station_eirp + terminal_antenna_gain + coding_gain + k_boltzmann
losses      = free_space_losses + additional_losses + 10 * np.log10(brightness_temp_est)
#losses      = free_space_losses + 2 + 10 * np.log10(brightness_temp_est)    # FSL, Additional losses, Rx temperature
c_to_no     = gains - losses
eb_to_no    = c_to_no # - 10 * np.log10(bitrate)
excess_db   = eb_to_no - scheme_required_gamma['BPSK']
allowed_bitrate = np.power(10, excess_db / 10)

fig, ax = plt.subplots(1, figsize=(8, 4))


plt.plot(elevation_angle, allowed_bitrate/1e6, color="indianred", label="Bitrate")
## We can't increase the bitrate indefinetily bcoz we are bandwidth limited. Next we plot the upper bound
maximum_bitrate = bw * scheme_efficiency['BPSK'] * coding_rate
plt.plot(elevation_angle, [maximum_bitrate/ 1e6]*len(elevation_angle), label = "Maximum theoretical bitrate", linestyle = "--")
plt.title("Maximum bitrate allowed to maintain BER $<10^{}$ for BPSK modulation".format(int(np.log10(target_ber))))
plt.xlabel("Elevation angle [deg]")
plt.ylabel("Maximum bitrate [Mbps]")
plt.legend()

plt.yscale('log')
ax.set_xlim(90, 0)

ax.yaxis.set_major_locator(plt.FixedLocator([1, 2, 5, 10, 20, 50, 100, 200, 500]))
ax.yaxis.set_major_formatter(plt.FixedFormatter([1, 2, 5, 10, 20, 50, 100, 200, 500]))
plt.grid()

plt.tight_layout()

plt.savefig("../output/maximum_bitrate_uplink.png")
plt.savefig("../output/maximum_bitrate_uplink.svg")

plt.show()


