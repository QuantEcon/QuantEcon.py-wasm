# This file is not meant for public use and will be removed v0.8.0.
# Use the `quantecon` namespace for importing the objects
# included below.

import warnings
from . import _lss


__all__ = ['LinearStateSpace', 'simulate_linear_model']


def __dir__():
    return __all__


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(
                "`quantecon_wasm.lss` is deprecated and has no attribute "
                f"'{name}'."
            )

    warnings.warn(f"Please use `{name}` from the `quantecon` namespace, the"
                  "`quantecon_wasm.lss` namespace is deprecated. You can use"
                  f" the following instead:\n `from quantecon_wasm import {name}`.",
                  category=DeprecationWarning, stacklevel=2)

    return getattr(_lss, name)
