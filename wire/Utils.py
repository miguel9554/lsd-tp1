def float_to_string(number: float, decimals: int = 3):
    if 1e-15 <= number < 1e-12:
        return '{number:.{decimals}f}f'.format(decimals=decimals, number=number/1e-15)
    if 1e-12 <= number < 1e-9:
        return '{number:.{decimals}f}p'.format(decimals=decimals, number=number/1e-12)
    if 1e-9 <= number < 1e-6:
        return '{number:.{decimals}f}n'.format(decimals=decimals, number=number/1e-9)
    if 1e-6 <= number < 1e-3:
        return '{number:.{decimals}f}u'.format(decimals=decimals, number=number/1e-6)
    if 1e-3 <= number < 1:
        return '{number:.{decimals}f}m'.format(decimals=decimals, number=number/1e-3)
    if 1 <= number < 1e3:
        return '{number:.{decimals}f}'.format(decimals=decimals, number=number)
    if 1e3 <= number < 1e6:
        return '{number:.{decimals}f}K'.format(decimals=decimals, number=number/1e3)
    if 1e6 <= number < 1e9:
        return '{number:.{decimals}f}Meg'.format(decimals=decimals, number=number/1e6)
    if 1e9 <= number < 1e12:
        return '{number:.{decimals}f}G'.format(decimals=decimals, number=number/1e9)
    if 1e12 <= number < 1e15:
        return '{number:.{decimals}f}T'.format(decimals=decimals, number=number/1e12)
    else:
        return str(number)
