from functools import singledispatch
from typing import List
import pandas as pd
import numpy as np


@singledispatch
def coerce_to_iterable(x) -> List:
    return x


@coerce_to_iterable.register
def coerce_to_iterable_int(x: int) -> List:
    return [x]


@coerce_to_iterable.register
def coerce_to_iterable_str(x: str) -> List:
    return [x]


def all_integers_or_character(x):
    try:
        decimals = np.modl(x, 1)
    except TypeError:
        return None
    return np.sum(decimals) > 0