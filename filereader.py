from astropy.io import fits
def fitsreader(filename):
    f = fits.open(filename)
    return f[0].header
