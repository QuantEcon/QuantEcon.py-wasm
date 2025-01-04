"""
Utilities to support Numba jitted functions

"""
import numpy as np

def _numba_linalg_solve(a, b):  # pragma: no cover
    try:
        r = np.linalg.solve(a, b)
        b[:] = r
        return 0
    except np.linalg.LinAlgError:
        return -1


def comb_jit(N, k):
    """
    Numba jitted function that computes N choose k. Return `0` if the
    outcome exceeds the maximum value of `np.intp` or if N < 0, k < 0,
    or k > N.

    Parameters
    ----------
    N : scalar(int)

    k : scalar(int)

    Returns
    -------
    val : scalar(int)

    """
    # From scipy.special._comb_int_long
    # github.com/scipy/scipy/blob/v1.0.0/scipy/special/_comb.pyx
    INTP_MAX = np.iinfo(np.intp).max
    if N < 0 or k < 0 or k > N:
        return 0
    if k == 0:
        return 1
    if k == 1:
        return N
    if N == INTP_MAX:
        return 0

    M = N + 1
    nterms = min(k, N - k)

    val = 1

    for j in range(1, nterms + 1):
        # Overflow check
        if val > INTP_MAX // (M - j):
            return 0

        val *= M - j
        val //= j

    return val
