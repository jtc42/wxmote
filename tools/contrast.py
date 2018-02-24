# Contrast polynomial
def c_poly(x, n):
    return (x**n)*(0.5**(1-n))


# Contrast function
def c_func(x, n):
    # Inverse direction of curve above 50% brightness (gives S-shape)
    if x > 0.5:
        return 1 - c_poly(1-x, n)
    else:
        return c_poly(x, n)


# Apply contrast function to a colour value
def apply_contrast(rgb, contrast):
    return [int(c_func(c/255., contrast) * 255) for c in rgb]