import wx


def util_lines_intersection(from1, to1, from2, to2, include_extend=False, use_float=False):
    """
    Function to calculate the intersection point between two lines.
    line1: from1 -> to1, line2: from2-> to2. sometimes the intersection located the line extend
    this will be calculated if include_extend is true.
    :param from1: Point
    :param to1: Point
    :param from2: Point
    :param to2: Point
    :param include_extend: if calculate the intersection on the extend
    :param use_float: if use float data type
    :return: Point or RealPoint
    """
    # create line 1 info
    _a1 = to1.y - from1.y
    _b1 = from1.x - to1.x
    _c1 = -_a1 * from1.x - _b1 * from1.y
    # create line 2 info
    _a2 = to2.y - from2.y
    _b2 = from2.x - to2.x
    _c2 = -_a2 * from2.x - _b2 * from2.y
    # check, whether the lines are parallel...
    _ka = _a1 / _a2
    _kb = _b1 / _b2
    if _ka == _kb: return None
    # find intersection point
    _xi = ((_b1 * _c2 - _c1 * _b2) / (_a1 * _b2 - _a2 * _b1))
    _yi = (-(_a1 * _c2 - _a2 * _c1) / (_a1 * _b2 - _a2 * _b1))

    if not include_extend:
        if (((from1.x - _xi) * (_xi - to1.x) >= 0) and
                ((from2.x - _xi) * (_xi - to2.x) >= 0) and
                ((from1.y - _yi) * (_yi - to1.y) >= 0) and
                ((from2.y - _yi) * (_yi - to2.y) >= 0)):
            return wx.Point(_xi, _yi) if not use_float else wx.RealPoint(_xi, _yi)
        else:
            return None
    else:
        return wx.Point(_xi, _yi) if not use_float else wx.RealPoint(_xi, _yi)


def intersection(ap1, ap2, bp1, bp2, use_extend=True, use_float=False):
    _k1 = (ap2.y - ap1.y) / (ap2.x - ap1.x)
    _k2 = (bp2.y - bp1.y) / (bp2.x - bp1.x)
    _b1 = ap2.y - _k1 * ap2.x
    _b2 = bp2.y - _k2 * bp2.x
    if _k1 == _k2:
        return None
    _p_x = (_b2 - _b1) / (_k1 - _k2)
    _p_y = _k1 * _p_x + _b1
    if use_float:
        return wx.RealPoint(_p_x, _p_y)
    return wx.Point(_p_x, _p_y)


_ap1 = wx.Point(0, 0)
_ap2 = wx.Point(4, 4)

_bp1 = wx.Point(0, 30)
_bp2 = wx.Point(30, 0)

print(intersection(_ap1, _ap2, _bp1, _bp2), util_lines_intersection(_ap1, _ap2, _bp1, _bp2, True))
