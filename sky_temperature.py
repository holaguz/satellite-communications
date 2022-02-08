import matplotlib.pyplot as plt
import numpy as np
import sys

# Empirical sky temperature data at 10 GHz
# https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.372-15-202109-I!!PDF-E.pdf
data_points = np.array([
    [0, 150],
    [5, 30],
    [10, 17],
    [20, 9],
    [30, 6],
    [60, 4],
    [90, 3]]
).transpose()

def get_sky_temperature(elevation_angle: float):
    return np.interp(elevation_angle, data_points[0], data_points[1])

if __name__ == "__main__":

    if(len(sys.argv) >= 2):
        elevation_angle = int(sys.argv[1])
        print(get_sky_temperature(elevation_angle))
        sys.exit()

    plt.close()
    plt.figure(figsize = (8, 4))

    plt.title("Brightness temperature vs. elevation angle\n(clean air, ${7.5g/m^3}$ water vapour concentration, freq. 10 GHz)")
    plt.xlabel("Elevation angle [deg]")
    plt.ylabel("Brightness temperature [K]")

    plt.plot(data_points[0], data_points[1], 'x',   color="indianred",  markersize=8, label="Data points")
    # plt.plot(data_points[0], data_points[1], '--',  color="dodgerblue", label="Linear interpolation")
    t = np.arange(0, 91, 5)
    plt.plot(t, get_sky_temperature(t), '--',  color="dodgerblue", label="Linear interpolation")
    plt.legend()

    plt.yscale("log")

    xlocs = np.append(np.arange(0, 91, 15), data_points[0])
    ylocs = np.append(np.arange(0, 101, 25), data_points[1])

    plt.xticks(xlocs, xlocs)
    plt.yticks(ylocs, ylocs)

    plt.autoscale("auto")
    plt.grid(True, axis="both")
    plt.tight_layout()

    plt.savefig ("../output/sky_temperature_vs_angle.svg")
    plt.savefig ("../output/sky_temperature_vs_angle.png")

    plt.show()