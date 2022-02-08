import numpy as np
from scipy import constants
import matplotlib as mpl
import matplotlib.ticker
import matplotlib.pyplot as plt
import sys

re = 6371E3;

def distance(phi_l_deg, h):
    phi_l_rad = phi_l_deg * np.pi / 180.0;
    return np.sqrt((re * np.sin(phi_l_rad))**2 + 2 * re * h + h**2) - re * np.sin(phi_l_rad)

def fsl(d, f):
    c = constants.speed_of_light
    return 20.0 * np.log10( 4 * np.pi * f * d / c )

def elevation_angle_to_earth_angle(elevation_angle: float, orbit_height: float):
    elevation_angle = elevation_angle * np.pi / 180
    return 180 / np.pi * (np.arccos(re / (re + orbit_height) * np.cos(elevation_angle)) - elevation_angle)

if __name__ == "__main__":

    plt.close()

    h = 650E3;
    a = np.linspace(90, 0, 19);
    z = distance(a, h);

    if(len(sys.argv) >= 3):
        elevation_angle = int(sys.argv[1])
        f               = int(sys.argv[2])
        print(fsl(10**3 * distance(elevation_angle, h), 10**9 * f))
        exit()

    fig, ax = plt.subplots(1)
    ax.plot(a, z / 1e3, 'rx')
    ax.invert_xaxis()
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base = 10.0))

    ax.grid(True, which = 'major')
    ax.grid(True, which = 'minor', axis = 'y')
    ax.minorticks_on()

    plt.title   ("Distance between satellite and base station")
    plt.xlabel  ("Elevation angle $\phi_l$ [deg]")
    plt.ylabel  ("Distance [km]")

    plt.savefig ("../output/distance.svg")
    plt.savefig ("../output/distance.png")

    plt.show()

    fig, ax = plt.subplots(1)
    losses = fsl(z, 7.8E9)
    ax.plot(a, losses, 'rx')
    ax.invert_xaxis()
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base = 10.0))

    ax.grid(True, which = 'major')
    ax.grid(True, which = 'minor', axis = 'y')
    ax.minorticks_on()

    plt.title   ("Free space losses")
    plt.xlabel  ("Elevation angle $\phi_l$ [deg]")
    plt.ylabel  ("FSL [dB]")

    plt.savefig ("../output/fsl.svg")
    plt.savefig ("../output/fsl.png")

    plt.show()