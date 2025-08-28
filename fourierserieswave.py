import numpy as np
import constants as const

def fourierserieswave( coeffs, x, t ):
    """
    Args:
        coeffs (array-like): Fourier coefficients [v, a1, b1, a2, b2, ..., an, bn].
        x (float or array-like): Position(s) at which to evaluate the series.

    Returns:
        float or np.ndarray: Value of the Fourier series at x-v*t.
    """    
    
    coeffs = np.asarray(coeffs)
    v = coeffs[0]
    n_terms = (len(coeffs) - 2) // 2
    x_shifted = x - v * t
    result = coeffs[1]

    for n in range(1, n_terms):
        a_n = coeffs[2 * n]
        b_n = coeffs[2 * n + 1]
        result += a_n * np.cos(2*np.pi*float(n)/const.P * x_shifted) + b_n * np.sin( 2*np.pi*float(n)/const.P * x_shifted )

    return result

