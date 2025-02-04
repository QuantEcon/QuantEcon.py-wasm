
"""
Tests for inequality.py

"""

import numpy as np
from numpy.testing import assert_allclose, assert_raises
from scipy.stats import linregress
from quantecon_wasm import lorenz_curve, gini_coefficient, \
     shorrocks_index, rank_size


def test_lorenz_curve():
    """
    Tests `lorenz` function, which calculates the lorenz curve

    An income distribution where everyone has almost the same wealth should
    be similar to a straight line

    An income distribution where one person has almost the wealth should
    be flat and then shoot straight up when it approaches one
    """
    n = 3000

    # Almost Equal distribution
    y = np.repeat(1, n) + np.random.normal(scale=0.0001, size=n)
    cum_people, cum_income = lorenz_curve(y)
    assert_allclose(cum_people, cum_income, rtol=1e-03)

    # Very uneven distribution
    y = np.repeat(0.001, n)
    y[4] = 100000
    pop_cum, income_cum = lorenz_curve(y)
    expected_income_cum = np.repeat(0., n + 1)
    expected_income_cum[-1] = 1.
    assert_allclose(expected_income_cum, income_cum, atol=1e-4)


def test_gini_coeff():
    """
    Tests how the function `gini_coefficient` calculates the Gini coefficient
    with the Pareto and the Weibull distribution.

    Analytically, we know that Pareto with parameter `a` has
    G = 1 / (2*a - 1)

    Likewise, for the Weibull distribution with parameter `a` we know that
    G = 1 - 2**(-1/a)

    """
    n = 10000

    # Tests Pareto: G = 1 / (2*a - 1)
    a = np.random.randint(2, 15)
    expected = 1 / (2 * a - 1)

    y = (np.random.pareto(a, size=n) + 1) * 2
    coeff = gini_coefficient(y)
    assert_allclose(expected, coeff, rtol=1e-01)

    # Tests Weibull: G = 1 - 2**(-1/a)
    a = np.random.randint(2, 15)
    expected = 1 - 2 ** (-1 / a)

    y = np.random.weibull(a, size=n)
    coeff = gini_coefficient(y)
    assert_allclose(expected, coeff, rtol=1e-01)


def test_shorrocks_index():
    """
    Test Shorrocks mobility index function against the example used in 'Wealth
    distribution and social mobility in the US: A quantitative approach'
    (Benhabib, Bisin, Luo, 2017).''
    https://www.econ.nyu.edu/user/bisina/RevisionAugust.pdf
    """

    # Construct the mobility matrix from Benhabib et al.
    P = [[0.222, 0.222, 0.215, 0.187, 0.081, 0.038, 0.029, 0.006],
         [0.221, 0.220, 0.215, 0.188, 0.082, 0.039, 0.029, 0.006],
         [0.207, 0.209, 0.210, 0.194, 0.090, 0.046, 0.036, 0.008],
         [0.198, 0.201, 0.207, 0.198, 0.095, 0.052, 0.040, 0.009],
         [0.175, 0.178, 0.197, 0.207, 0.110, 0.067, 0.054, 0.012],
         [0.182, 0.184, 0.200, 0.205, 0.106, 0.062, 0.050, 0.011],
         [0.123, 0.125, 0.166, 0.216, 0.141, 0.114, 0.094, 0.021],
         [0.084, 0.084, 0.142, 0.228, 0.170, 0.143, 0.121, 0.028]]

    expected = 0.98  # result from paper
    index = shorrocks_index(P)
    assert_allclose(expected, index, rtol=1e-2)


def test_rank_size():
    """
    Tests `rank_size` function, which generates rank-size data for
    a Pareto distribution.

    The rank-size plot for a sample drawn from a Pareto distribution
    should be a straight line.

    The length of the `rank_data` array should be within (c x 100)%
    of the size of the distribution.
    """

    rng = np.random.default_rng(15)
    sample_size = 10000
    c = 0.74

    # Tests Pareto; r_squared ~ 1
    pareto_draw = np.exp(rng.exponential(scale=1.0, size=sample_size))
    rank_data, size_data = rank_size(pareto_draw, c=c)

    assert len(rank_data) == len(size_data)
    assert_allclose(c*sample_size, len(rank_data), rtol=1e-3)

    _, _, r_value, _, _ = linregress(np.log(rank_data), np.log(size_data))
    r_sqval = r_value**2

    assert_allclose(r_sqval, 1, rtol=1e-3)

    # Tests Exponential; r_squared < 1
    z = rng.standard_normal(sample_size)

    exp_draw = np.exp(z)
    rank_data_exp, size_data_exp = rank_size(exp_draw, c=c)

    _, _, r_value_exp, _, _ = linregress(np.log(rank_data_exp),
                                         np.log(size_data_exp))
    r_sqval_exp = r_value_exp**2

    assert_raises(AssertionError, assert_allclose, r_sqval_exp, 1, rtol=1e-3)

