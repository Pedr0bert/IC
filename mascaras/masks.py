from diffractio import degrees, mm, um
from diffractio import np, plt
from diffractio.scalar_sources_XY import Scalar_source_XY


N = 2
K = 2

x0 = np.linspace(-1*mm, 1*mm, 512)
y0 = np.linspace(-1*mm, 1*mm, 512)
wavelength = 0.6238*um

u = Scalar_source_XY(x=x0, y=y0, wavelength=wavelength)

u.laguerre_beam(A=1,
                n=N,
                l=K,
                r0=(0*um, 0*um),
                w0=250*um,
                z0=0,
                z=0.01*um)

title = r'$n=%d, k=%d$' % (N, K)
u.draw(kind='field', title=title)

