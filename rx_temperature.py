import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec
import matplotlib.ticker
import pandas as pd
from sky_temperature import get_sky_temperature

def to_db(value: float):
    return 10 * np.log10(value)

def to_lineal_gain(value: float):
    return np.power(10, value / 10)

assert(to_db(to_lineal_gain(10)) == 10)

def nf_to_temperature(nf: float):
    return 290.0 * ( to_lineal_gain(nf) - 1)

def get_rx_temperature(elevation_angle, Tphysical):
    print("Simulating with Tphys = {}".format(Tphysical))
    # Left plane
    Tsky = get_sky_temperature(elevation_angle)

    antenna_efficiency  = 60 / 100
    left_plane_losses   = 0.2 # perdidas a la izquierda del plano de referencia [dB]

    Tantenna = 1.0 / to_lineal_gain(left_plane_losses) * (Tsky * antenna_efficiency + Tphysical * (to_lineal_gain(left_plane_losses) - antenna_efficiency))
    # Temperatura a la derecha del plano de referencia -- Todas las ganancias y perdidas se expresan en dB
    Tr = 0

    # Multiplicatoria de ganancias
    K = 1

    ## LNB ##
    G_LNB   = 50
    NF_LNB  = 1.62
    T_LNB   = nf_to_temperature(NF_LNB)

    ## TL1 ##
    L_TL1 = 1

    ## TL2 ##
    L_TL2 = 1

    ## ADC ##
    T_ADC = 0   # Ignorado en el análisis

    ## Amplifier 1 ##
    G_AMP1  = 0
    NF_AMP1 = 6
    T_AMP1  = nf_to_temperature(NF_AMP1)

    # LNB
    Tr += T_LNB
    print("[0]: {}\t".format(Tr))

    # Transmission Line 1
    K *= to_lineal_gain(G_LNB)
    dt = ( to_lineal_gain( L_TL1 ) - 1 ) * Tphysical / K
    Tr += dt
    print("[1]: {}\t deltaT = {}, deltaT/T = {:1.2f}%".format(Tr, dt,100 * dt / (Tr - dt)))

    # Amplifier
    K /= to_lineal_gain(L_TL1)
    dt = T_AMP1 / K
    Tr += dt
    print("[2]: {}\t deltaT = {}, deltaT/T = {:1.2f}%".format(Tr, dt,100 * dt / (Tr - dt)))

    # Transmission Line 2
    K *= to_lineal_gain(G_AMP1)
    dt = ( to_lineal_gain( L_TL2 ) - 1 ) * Tphysical / K
    Tr += dt
    print("[3]: {}\t deltaT = {}, deltaT/T = {:1.2f}%".format(Tr, dt,100 * dt / (Tr - dt)))

    # ADC
    K *= 1.0 / to_lineal_gain(L_TL2)
    dt = T_ADC / K
    Tr += dt
    print("[4]: {}\t deltaT = {}, deltaT/T = {:1.2f}%\n".format(Tr, dt,100 * dt / (Tr - dt)))

    Teq = Tr + Tantenna
    return Teq

if __name__ == "__main__":
    elevation_angle         = np.arange(0, 91, 1)
    physical_temperature    = np.array([273.15, 293.15, 303.15])

    temps = pd.DataFrame(
        columns = [
            "Physical",
            "System"
        ]
    )

    temps.Physical  = physical_temperature
    temps.System    = temps.apply(
        lambda row:
            get_rx_temperature(elevation_angle, row[0]), axis = 1
    )

    fig = plt.figure(figsize = (8, 4))
    gs = matplotlib.gridspec.GridSpec(1, 3)

    ax0 = plt.subplot(gs[0, 0:2])
    ax1 = plt.subplot(gs[0, 2:3])
    
    ax0.set_xlim(90, 15)
    ax0.set_yscale('log')
    
    ax1.set_xlim(15, 0)
    ax1.set_yscale('log')

    fig.suptitle("Receiver temperature vs. elevation angle")
    fig.supylabel("Equivalent temperature [K]")
    fig.supxlabel("Elevation angle [deg]")

    # ax0.set_title("Receiver temperature vs. elevation angle")
    # ax0.set_xlabel("Elevation angle [deg]")
    
    ax0.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax0.yaxis.set_major_locator(plt.MultipleLocator(5))
    
    ax0.yaxis.set_minor_locator(plt.MultipleLocator(1))
    ax0.yaxis.set_minor_formatter(matplotlib.ticker.ScalarFormatter())
    ax0.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax0.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    ax1.yaxis.set_major_locator(plt.MultipleLocator(20))
    ax1.yaxis.set_minor_locator(plt.MultipleLocator(5))
    ax1.yaxis.set_minor_formatter(matplotlib.ticker.ScalarFormatter())
    ax1.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax1.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    for entry in temps.values:
        ss = elevation_angle[15:90]
        ax0.plot(ss, entry[1][15:90], label = "Rx Temperature (phys. {} deg C)".format(entry[0] - 273.15))

    ax0.legend()
    ax0.autoscale(axis='y')

    for entry in temps.values:
        ss = elevation_angle[0:20]
        ax1.plot(ss, entry[1][0:20], label = "Rx Temperature (phys. {} deg C)".format(entry[0]))

    ax1.autoscale(axis='y')

    ax0.grid(True, axis="both", which="both")
    ax1.grid(True, axis="both", which="both")

    fig.savefig ("../output/rx_temperature_vs_angle.png")
    fig.savefig ("../output/rx_temperature_vs_angle.svg")

    fig.tight_layout()

    plt.show()

