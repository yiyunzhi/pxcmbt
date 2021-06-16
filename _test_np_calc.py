import numpy as np
from wxgraph.util_bbox import *


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    # return np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)


def section_middle_split(length, min_dist):
    if length <= min_dist:
        return 1
    else:
        _half = length / 2
        _section = 1
        while _half > min_dist:
            _section += 1
            _half /= 2
        return _section


class Shape:
    def __init__(self):
        self.boundingBox = from_points([(0, 0), (100, 100)])
        self.minConnPtDistance = 25

    def get_connection_points(self):
        # for rectangle shape
        _pts = list()
        _w = self.boundingBox.width
        _h = self.boundingBox.height
        _w_num_sections = section_middle_split(_w, self.minConnPtDistance)
        _h_num_sections = section_middle_split(_h, self.minConnPtDistance)
        # process h direction conn pts
        for i in range(_h_num_sections):
            _pts.append(((-1, 0), (self.boundingBox.left, self.boundingBox.center[1] + i * self.minConnPtDistance)))
            if i != 0:
                _pts.append(((-1, 0), (self.boundingBox.left, self.boundingBox.center[1] - i * self.minConnPtDistance)))
                _pts.append(((1, 0), (self.boundingBox.right, self.boundingBox.center[1] - i * self.minConnPtDistance)))
            _pts.append(((1, 0), (self.boundingBox.right, self.boundingBox.center[1] + i * self.minConnPtDistance)))
        for i in range(_w_num_sections):
            _pts.append(((0, 1), (self.boundingBox.center[0] + i * self.minConnPtDistance, self.boundingBox.top)))
            if i != 0:
                _pts.append(((0, 1), (self.boundingBox.center[0] - i * self.minConnPtDistance, self.boundingBox.top)))
                _pts.append(
                    ((0, -1), (self.boundingBox.center[0] - i * self.minConnPtDistance, self.boundingBox.bottom)))
            _pts.append(((0, -1), (self.boundingBox.center[0] + i * self.minConnPtDistance, self.boundingBox.bottom)))
        return _pts
    # def get_connection_point(self, pos):
    #     _areas, _area_nvs = self.get_connection_areas()
    #     _nv_idx = -1
    #     for idx, bb in enumerate(_areas):
    #         if bb.point_inside(pos):
    #             _nv_idx = idx
    #             break
    #     if _nv_idx != -1:
    #         _pt = [pos[0], pos[1]]
    #         _nvx, _nvy, _offset = _area_nvs[_nv_idx]
    #         if _nvx != 0:
    #             _pt[0] = _offset
    #         if _nvy != 0:
    #             _pt[1] = _offset
    #         return np.array(_pt), (_nvx, _nvy), self.connectionZoneTol
    #     else:
    #         return None, (0, 0), self.connectionZoneTol


if __name__ == '__main__':
    _shape = Shape()
    _shape.get_connection_points()
    # print(_shape.get_connection_point((5, 11)))
