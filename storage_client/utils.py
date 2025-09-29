import math


def coerce_string(value) -> str:
    if type(value) is float and math.isnan(value):
        return ""
    return value


def coerce_int(value) -> int:
    if type(value) is float and math.isnan(value):
        return 0
    return int(value)
