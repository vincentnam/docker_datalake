import sys

def isfloat(x):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True


sys.modules[__name__] = isfloat
