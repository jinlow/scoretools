from functools import singledispatch
from typing import List
import pandas as pd
import numpy as np


@singledispatch
def coerce_to_iterable(obj) -> List:
    return obj


@coerce_to_iterable.register
def coerce_to_iterable_int(obj: int) -> List:
    return [obj]


@coerce_to_iterable.register
def coerce_to_iterable_str(obj: str) -> List:
    return [obj]


def all_integers(obj):
    try:
        decimals = np.mod(obj, 1)
    except TypeError:
        return False
    return np.sum(decimals) == 0


# Snagged from is_dict_like from pandas.core.dtypes.inference
def is_dict_like(obj):
    dict_like_attrs = ("__getitem__", "keys", "__contains__")
    return (
        all(hasattr(obj, attr) for attr in dict_like_attrs)
        # [GH 25196] exclude classes
        and not isinstance(obj, type)
    )
