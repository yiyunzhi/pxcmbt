# ----------------------------------------------------------------------------
# Name:         BBox.py
# Purpose:
#
# Author:
#
# Created:
# Version:
# Date:
# Licence:
# Tags:         phoenix-port
# ----------------------------------------------------------------------------
"""
A Bounding Box object and assorted utilities , subclassed from a numpy array
"""

import numpy as N


class BBox(N.ndarray):
    """
    A Bounding Box object:

    Takes Data as an array. Data is any python sequence that can be turned into a
    2x2 numpy array of floats::

        [
        [MinX, MinY ],
        [MaxX, MaxY ]
        ]

    It is a subclass of numpy.ndarray, so for the most part it can be used as
    an array, and arrays that fit the above description can be used in its place.

    Usually created by the factory functions:

        asBBox

        and

        fromPoints

    """

    def __new__(subtype, data):
        """
        Takes Data as an array. Data is any python sequence that can be turned
        into a 2x2 numpy array of floats::

            [
            [MinX, MinY ],
            [MaxX, MaxY ]
            ]

        You don't usually call this directly. BBox objects are created with
        the factory functions:

        asBBox

        and

        fromPoints

        """
        _arr = N.array(data, N.float)
        _arr.shape = (2, 2)
        if _arr[0, 0] > _arr[1, 0] or _arr[0, 1] > _arr[1, 1]:
            # note: zero sized BB OK.
            raise ValueError("BBox values not aligned: \n minimum values must be less that maximum values")
        return N.ndarray.__new__(subtype, shape=_arr.shape, dtype=_arr.dtype, buffer=_arr)

    def overlaps(self, bb):
        """
        overlaps(bb):

        Tests if the given Bounding Box overlaps with this one.
        Returns True is the Bounding boxes overlap, False otherwise
        If they are just touching, returns True
        """

        if N.isinf(self).all() or N.isinf(bb).all():
            return True
        if ((self[1, 0] >= bb[0, 0]) and (self[0, 0] <= bb[1, 0]) and
                (self[1, 1] >= bb[0, 1]) and (self[0, 1] <= bb[1, 1])):
            return True
        else:
            return False

    def inside(self, bb):
        """
        inside(bb):

        Tests if the given Bounding Box is entirely inside this one.

        Returns True if it is entirely inside, or touching the
        border.

        Returns False otherwise
        """
        if ((bb[0, 0] >= self[0, 0]) and (bb[1, 0] <= self[1, 0]) and
                (bb[0, 1] >= self[0, 1]) and (bb[1, 1] <= self[1, 1])):
            return True
        else:
            return False

    def point_inside(self, point):
        """
        point_inside(point):

        Tests if the given Point is entirely inside this one.

        Returns True if it is entirely inside, or touching the
        border.

        Returns False otherwise

        Point is any length-2 sequence (tuple, list, array) or two numbers
        """
        if self[1, 0] >= point[0] >= self[0, 0] and self[1, 1] >= point[1] >= self[0, 1]:
            return True
        else:
            return False

    def merge(self, bb):
        """
        Joins this bounding box with the one passed in, maybe making this one bigger

        """
        if self.is_null():
            self[:] = bb
        elif N.isnan(bb).all():
            # BB may be a regular array, so I can't use IsNull
            pass
        else:
            if bb[0, 0] < self[0, 0]: self[0, 0] = bb[0, 0]
            if bb[0, 1] < self[0, 1]: self[0, 1] = bb[0, 1]
            if bb[1, 0] > self[1, 0]: self[1, 0] = bb[1, 0]
            if bb[1, 1] > self[1, 1]: self[1, 1] = bb[1, 1]

        return None

    def is_null(self):
        return N.isnan(self).all()

    # fixme: it would be nice to add setter, too.
    def _get_left(self):
        return self[0, 0]

    left = property(_get_left)

    def _get_right(self):
        return self[1, 0]

    right = property(_get_right)

    def _get_bottom(self):
        return self[0, 1]

    bottom = property(_get_bottom)

    def _get_top(self):
        return self[1, 1]

    top = property(_get_top)

    def _get_width(self):
        return self[1, 0] - self[0, 0]

    width = property(_get_width)

    def _get_height(self):
        return self[1, 1] - self[0, 1]

    height = property(_get_height)

    def _get_center(self):
        return self.sum(0) / 2.0

    center = property(_get_center)
    # This could be used for a make BB from a bunch of BBs

    # ~ def _getboundingbox(bboxarray): # lrk: added this
    # ~ # returns the bounding box of a bunch of bounding boxes
    # ~ upperleft = N.minimum.reduce(bboxarray[:,0])
    # ~ lowerright = N.maximum.reduce(bboxarray[:,1])
    # ~ return N.array((upperleft, lowerright), N.float)
    # ~ _getboundingbox = staticmethod(_getboundingbox)

    # Save the ndarray __eq__ for internal use.
    Array__eq__ = N.ndarray.__eq__

    def __eq__(self, bb):
        """
        __eq__(BB) The equality operator

        A == B if and only if all the entries are the same

        """
        if self.is_null() and N.isnan(bb).all():  ## BB may be a regular array, so I can't use IsNull
            return True
        else:
            return self.Array__eq__(bb).all()


def as_bbox(data):
    """
    returns a BBox object.

    If object is a BBox, it is returned unaltered

    If object is a numpy array, a BBox object is returned that shares a
    view of the data with that array. The numpy array should be of the correct
    format: a 2x2 numpy array of floats::

        [
        [MinX, MinY ],
        [MaxX, MaxY ]
        ]

    """

    if isinstance(data, BBox):
        return data
    arr = N.asarray(data, N.float)
    return N.ndarray.__new__(BBox, shape=arr.shape, dtype=arr.dtype, buffer=arr)


def from_points(points):
    """
    from_points (points).

    return the bounding box of the set of points in Points. Points can
    be any python object that can be turned into a numpy NX2 array of Floats.

    If a single point is passed in, a zero-size Bounding Box is returned.

    """
    _points = N.asarray(points, N.float).reshape(-1, 2)

    _arr = N.vstack((_points.min(0), _points.max(0)))
    return N.ndarray.__new__(BBox, shape=_arr.shape, dtype=_arr.dtype, buffer=_arr)


def from_bb_array(bb_array):
    """
    Builds a BBox object from an array of Bounding Boxes.
    The resulting Bounding Box encompases all the included BBs.

    The bb_array is in the shape: (Nx2x2) where BBarray[n] is a 2x2 array that represents a BBox
    """

    # upperleft = N.minimum.reduce(BBarray[:,0])
    # lowerright = N.maximum.reduce(BBarray[:,1])

    #   BBarray = N.asarray(BBarray, N.float).reshape(-1,2)
    #   arr = N.vstack( (BBarray.min(0), BBarray.max(0)) )
    bb_array = N.asarray(bb_array, N.float).reshape(-1, 2, 2)
    _arr = N.vstack((bb_array[:, 0, :].min(0), bb_array[:, 1, :].max(0)))
    return as_bbox(_arr)
    # return asBBox( (upperleft, lowerright) ) * 2


def null_bbox():
    """
    Returns a BBox object with all NaN entries.

    This represents a Null BB box;

    BB merged with it will return BB.

    Nothing is inside it.

    """

    arr = N.array(((N.nan, N.nan), (N.nan, N.nan)), N.float)
    return N.ndarray.__new__(BBox, shape=arr.shape, dtype=arr.dtype, buffer=arr)


def inf_bbox():
    """
    Returns a BBox object with all -inf and inf entries

    """

    arr = N.array(((-N.inf, -N.inf), (N.inf, N.inf)), N.float)
    return N.ndarray.__new__(BBox, shape=arr.shape, dtype=arr.dtype, buffer=arr)


def inflated_bbox(bb, inflate):
    return from_points([bb[0] - inflate, bb[1] + inflate])
