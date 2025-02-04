"""
Utilities to Support Random Operations and Generating Vectors and Matrices

"""

import numpy as np
from ..util import check_random_state, searchsorted


# Generating Arrays and Vectors #

def probvec(m, k, random_state=None, parallel=True):
    """
    Return m randomly sampled probability vectors of dimension k.

    Parameters
    ----------
    m : scalar(int)
        Number of probability vectors.

    k : scalar(int)
        Dimension of each probability vectors.

    random_state : int or np.random.RandomState/Generator, optional
        Random seed (integer) or np.random.RandomState or Generator
        instance to set the initial state of the random number generator
        for reproducibility. If None, a randomly initialized RandomState
        is used.

    Returns
    -------
    x : ndarray(float, ndim=2)
        Array of shape (m, k) containing probability vectors as rows.

    Examples
    --------
    >>> qe.random.probvec(2, 3, random_state=1234)
    array([[ 0.19151945,  0.43058932,  0.37789123],
           [ 0.43772774,  0.34763084,  0.21464142]])

    """
    if k == 1:
        return np.ones((m, k))

    # if k >= 2
    random_state = check_random_state(random_state)
    r = random_state.random(size=(m, k-1))
    x = np.empty((m, k))

    _probvec_cpu(r, x)

    return x

def _probvec(r, out):
    """
    Fill `out` with randomly sampled probability vectors as rows.

    The inputs must have the same shape except the last axis; the length of the last
    axis of `r` must be that of `out` minus 1, i.e., if out.shape[-1] is
    k, then r.shape[-1] must be k-1.

    Parameters
    ----------
    r : ndarray(float)
        Array containing random values in [0, 1).

    out : ndarray(float)
        Output array.

    """
    n = r.shape[0]
    r.sort()
    out[0] = r[0]
    for i in range(1, n):
        out[i] = r[i] - r[i - 1]
    out[n] = 1 - r[n - 1]


def _probvec_cpu(r, out):
    """
    Wrapper function to compute probability vectors for 2D input.

    Parameters
    ----------
    r : ndarray(float, ndim=1 or 2)
        Array of random values.

    Returns
    -------
    out : ndarray(float, ndim=1 or 2)
        Probability vectors. Shape will match `r` with an additional element along
        the last axis.
    """
    if r.ndim == 1:
        out = np.empty(r.shape[0] + 1, dtype=r.dtype)
        _probvec(r, out)
    elif r.ndim == 2:
        for i in range(r.shape[0]):
            _probvec(r[i], out[i])
    else:
        raise ValueError("Input `r` must be a 1D or 2D array.")


def sample_without_replacement(n, k, num_trials=None, random_state=None):
    """
    Randomly choose k integers without replacement from 0, ..., n-1.

    Parameters
    ----------
    n : scalar(int)
        Number of integers, 0, ..., n-1, to sample from.

    k : scalar(int)
        Number of integers to sample.

    num_trials : scalar(int), optional(default=None)
        Number of trials.

    random_state : int or np.random.RandomState/Generator, optional
        Random seed (integer) or np.random.RandomState or Generator
        instance to set the initial state of the random number generator
        for reproducibility. If None, a randomly initialized RandomState
        is used.

    Returns
    -------
    result : ndarray(int, ndim=1 or 2)
        Array of shape (k,) if num_trials is None, or of shape
        (num_trials, k) otherwise, (each row of) which contains k unique
        random elements chosen from 0, ..., n-1.

    Examples
    --------
    >>> qe.random.sample_without_replacement(5, 3, random_state=1234)
    array([0, 2, 1])
    >>> qe.random.sample_without_replacement(5, 3, num_trials=4,
    ...                                      random_state=1234)
    array([[0, 2, 1],
           [3, 4, 0],
           [1, 3, 2],
           [4, 1, 3]])

    """
    if n <= 0:
        raise ValueError('n must be greater than 0')
    if k > n:
        raise ValueError('k must be smaller than or equal to n')

    size = k if num_trials is None else (num_trials, k)

    random_state = check_random_state(random_state)
    r = random_state.random(size=size)

    if num_trials is None:
        result = _sample_without_replacement_single(n, r)
    else:
        result = np.array([_sample_without_replacement_single(n, trial_r) for trial_r in r])

    return result


def _sample_without_replacement_single(n, r):
    """
    Sample k integers without replacement from 0, ..., n-1 for a single trial.

    Parameters
    ----------
    n : int
        Total number of items.

    r : ndarray(float, ndim=1)
        Random values used to determine the selection.

    Returns
    -------
    out : ndarray(int, ndim=1)
        Array of k unique random elements chosen from 0, ..., n-1.
    """
    k = r.shape[0]
    pool = np.arange(n)
    out = np.empty(k, dtype=np.int64)

    # Logic to select without replacement
    for j in range(k):
        idx = int(np.floor(r[j] * (n - j)))  # Calculate index to select
        out[j] = pool[idx]
        pool[idx] = pool[n - j - 1]  # Replace used value with the last available

    return out


def draw(cdf, size=None):
    """
    Generate a random sample according to the cumulative distribution
    given by `cdf`. Jit-complied by Numba in nopython mode.

    Parameters
    ----------
    cdf : array_like(float, ndim=1)
        Array containing the cumulative distribution.

    size : scalar(int), optional(default=None)
        Size of the sample. If an integer is supplied, an ndarray of
        `size` independent draws is returned; otherwise, a single draw
        is returned as a scalar.

    Returns
    -------
    scalar(int) or ndarray(int, ndim=1)

    Examples
    --------
    >>> cdf = np.cumsum([0.4, 0.6])
    >>> qe.random.draw(cdf)
    1
    >>> qe.random.draw(cdf, 10)
    array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])

    """
    if isinstance(size, int):
        rs = np.random.random(size)
        out = np.empty(size, dtype=np.int_)
        for i in range(size):
            out[i] = searchsorted(cdf, rs[i])
        return out
    else:
        r = np.random.random()
        return searchsorted(cdf, r)
