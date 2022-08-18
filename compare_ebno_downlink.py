import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ber_psk import search_ber_psk
from ber_qam import search_ber_qam
from fsl_vs_phi_l import distance, fsl, elevation_angle_to_earth_angle
from sky_temperature import get_sky_temperature
from ber_psk import BER
from rx_temperature import get_rx_temperature

def pass_time(elevation_angle: float):
    te = 23*60*60   + 56*60 + 4
    ts = 1*60*60    + 36*60 + 32.5
    angle = elevation_angle_to_earth_angle(elevation_angle, 650E3)
    return angle / 180 * (ts / (1 - ts/te))
 
target_ber = 10**-5

scheme_required_gamma = dict()
scheme_required_gamma['BPSK']   = search_ber_psk(target_ber, 2, 1/100)
scheme_required_gamma['QPSK']   = search_ber_psk(target_ber, 4, 1/100)
scheme_required_gamma['8-QAM']  = search_ber_qam(target_ber, 8, 1/100)
scheme_required_gamma['16-QAM'] = search_ber_qam(target_ber, 16, 1/100)
scheme_required_gamma['32-QAM'] = search_ber_qam(target_ber, 32, 1/100)

scheme_efficiency = dict()
scheme_efficiency['BPSK']       = 1
scheme_efficiency['QPSK']       = 2
scheme_efficiency['8-QAM']      = np.sqrt(8)
scheme_efficiency['16-QAM']     = 4
scheme_efficiency['32-QAM']     = np.sqrt(32)

# Dataframe for storing schemes performance
df = pd.DataFrame(columns=['Scheme', 'Flyover time', 'Throughput'])

# System variables
orbit_height            = 600E3;
freq                    = (7.25 + 7.75) * 0.5E9;
bitrate                 = 70E6;
k_boltzmann             = -10*np.log10(1.38064852E-23)
system_phys_temperature = 300
coding_rate             = 223 / 255

elevation_angle         = np.arange(0, 90.2, 0.2)
receiver_temperature    = get_rx_temperature(elevation_angle, system_phys_temperature)
distance_to_satellite   = distance(elevation_angle, orbit_height)
free_space_losses       = fsl(distance_to_satellite, freq)

satellite_eirp          = 0 + 6.9    # 0 dBw + 6.9 dBi
coding_gain             = 5
terminal_antenna_gain   = 47

additional_losses       = 1.5 + 4 - 1.4

gains       = satellite_eirp + terminal_antenna_gain + coding_gain + k_boltzmann
losses      = free_space_losses + additional_losses + 10 * np.log10(receiver_temperature)
c_to_no     = gains - losses
eb_to_no    = c_to_no - 10 * np.log10(bitrate)

fig1, top_ax = plt.subplots(1, figsize=(8, 4))
fig2, bot_ax = plt.subplots(1, figsize=(8, 4))

###### Plot Eb/No ######
top_ax.plot(elevation_angle, eb_to_no, color="indianred", label="$E_b/N_0$")

top_ax.set_title("$E_b/N_0$ vs. elevation angle, and threshold elevation angle\nto achieve BER $<10^{}$ for different modulation schemes".format(int(np.log10(target_ber))))

top_ax.set_xlabel("Elevation angle [deg]")
top_ax.set_ylabel("$E_b/N_0$")
########################

# Evaluate schemes performance
for scheme, gamma in scheme_required_gamma.items():
    # Find angle at which the scheme satisfies the Eb/No requirement
    intersect = np.argmin( np.abs(eb_to_no - gamma) )
    intersect = elevation_angle[intersect]

    arrowprops = dict(facecolor='black', arrowstyle='->')

    # Check if the requirement is within the plot bounds
    if(intersect < 90 and intersect > min(elevation_angle)):
        # Annotate the result on the plot
        top_ax.annotate(scheme, (intersect, gamma), (intersect, gamma - 2), fontsize=14, arrowprops=arrowprops)

        obj = {
            "Scheme"        : scheme,
            "Flyover time"  : pass_time(intersect),
            "Throughput"    : pass_time(intersect) * scheme_efficiency[scheme],
            "Required"      : gamma}
        df = df.append(obj, ignore_index=True)
        # print(scheme, intersect)

        # Repeat for 4-dB margin
        intersect = np.argmin( np.abs(eb_to_no - gamma - 4) )
        intersect = elevation_angle[intersect]
        if intersect < 90 and intersect > min(elevation_angle):
            # print(scheme, intersect)
            obj = {
                "Scheme"        : scheme + ' (4 dB margin)',
                "Flyover time"  : pass_time(intersect),
                "Throughput"    : pass_time(intersect) * scheme_efficiency[scheme],
                "Required"      : gamma + 4}
            df = df.append(obj, ignore_index=True)

df = df.sort_values('Required')
text = []
for scheme in df.values:
    text.append(scheme[0] + ": " + "{:2.1f}".format(scheme[3]) + " dB")

# Sort the schemes performance by their throughput
df = df.sort_values('Throughput')

# Correct the throughput by the coding rate
df['Throughput'] *= coding_rate

# Bar plot
if not df.empty:
    df.plot('Scheme', 'Throughput', ax = bot_ax, kind='bar')
    for i, [scheme, req] in enumerate(df[['Scheme', 'Throughput']].values):
        bot_ax.text(i, req, int(req), horizontalalignment='center', verticalalignment='bottom')

bot_ax.set_xlabel('')
bot_ax.set_title("Data throughput per unit bandwidth")
bot_ax.set_ylabel("Bits/Hz")

# Plot schemes thresholds
props = dict(boxstyle='round', facecolor='white', alpha=0.5,)

text_string = ""
while text:
    text_string += text.pop() + '\n'
text_string = text_string[:-1]
bot_ax.text(0.02, 0.5,
            text_string,
            transform=bot_ax.transAxes, fontsize=14, verticalalignment='center', bbox=props)


# Plot throughput equation text
bot_ax.text(0.02, 0.85,
            "$throughput = flyover\ time * bandwidth\ efficiency$",
            transform=bot_ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)

#Rotate x labels
for label in bot_ax.xaxis.get_ticklabels():
    label.set_rotation(11.25)

top_ax.xaxis.set_major_locator(plt.MultipleLocator(5))
top_ax.yaxis.set_major_locator(plt.MultipleLocator(1))
top_ax.set_xlim(90, 20)
top_ax.set_ylim(5, 16)
top_ax.legend()
top_ax.grid(True, which="major", axis="both")
top_ax.grid(True, which="minor", axis="y")

#Show minor grid
# top_ax.minorticks_on()

fig1.tight_layout()
fig1.savefig ("output/ebno_vs_angle.svg")
fig1.savefig ("output/ebno_vs_angle.png")

fig2.tight_layout()
fig2.savefig ("output/data_throughput.svg")
fig2.savefig ("output/data_throughput.png")

plt.show()
