from functools import singledispatch
from typing import List
import pandas as pd


@singledispatch
def coerce_to_iterable(x) -> List:
    return x


@coerce_to_iterable.register
def coerce_to_iterable_int(x: int) -> List:
    return [x]


@coerce_to_iterable.register
def coerce_to_iterable_str(x: str) -> List:
    return [x]
