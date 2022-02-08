import matplotlib.pyplot as plt
import numpy as np

ah = 0.00454
av = 0.00395
bh = 1.327
bv = 1.310

R = 55
att_per_km = 0.5 * ( ah * np.power(R, bh) + av * np.power(R, bv)  )
print(att_per_km)

D_0 = 35 * np.exp(-0.015 * R)
L = 6.9

att_001 = att_per_km * L / (1 + L / D_0)

p = np.linspace(0.01, 2, 1000)
att_p = att_001 * np.power(p, -0.546 -0.043 * np.log10(p))

plt.plot(100 * p, att_p)
plt.show()