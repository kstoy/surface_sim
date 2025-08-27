import numpy as np

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
    n_terms = (len(coeffs) - 1) // 2
    x_shifted = x - v * t
    result = 0 # a0 is 0

    for n in range(1, n_terms):
        a_n = coeffs[2 * n]
        b_n = coeffs[2 * n + 1]
        result += a_n * np.cos(n * x_shifted) + b_n * np.sin(n * x_shifted)

    return result

