from .draw_object import DrawObject
from .draw_object_group import DrawObjectGroup
from .draw_object_polygon import DrawObjectPolygon
from .draw_object_text import DrawObjectScaledText, DrawObjectScaledTextBox
from .draw_object_circle import DrawObjectCircle
from .draw_object_rectellipse import DrawObjectEllipse, DrawObjectRectangle
from .draw_object_arc import DrawObjectArc
from .draw_object_circle import DrawObjectCircle
from .draw_object_line import DrawObjectLine
from .draw_object_arrow import DrawObjectArrow
from .draw_object_arrow_line import DrawObjectArrowLine
from .draw_object_point import DrawObjectPoint
from .draw_object_pointset import DrawObjectPointSet
from .draw_object_spline import DrawObjectSpline
from .draw_object_squarpoint import DrawObjectSquarePoint
from .wxcanvas import WxCanvas
import wxgraph.events as WxGEvent


def __make_canvas_add_methods():
    _prefix = 'DrawObject'
    _class_names = ["Circle", "Ellipse", "Arc", "Rectangle", "ScaledText", "Polygon",
                    "Line", "Text", "PointSet", "Point", "Arrow", "ArrowLine", "ScaledTextBox",
                    "SquarePoint", "Bitmap", "ScaledBitmap", "Spline", "Group"]
    for class_name in _class_names:
        _klass = globals()[_prefix + class_name]

        def get_add_shape_method(klass=_klass):
            def add_shape(self, *args, **kwargs):
                _object = klass(*args, **kwargs)
                self.add_object(_object)
                return _object

            return add_shape

        _add_shape_method = get_add_shape_method()
        _method_name = "add_" + class_name.lower()
        setattr(WxCanvas, _method_name, _add_shape_method)
        docstring = "Creates %s and adds its reference to the canvas.\n" % class_name
        docstring += "Argument protocol same as %s class" % class_name
        if _klass.__doc__:
            docstring += ", whose docstring is:\n%s" % _klass.__doc__
        WxCanvas.__dict__[_method_name].__doc__ = docstring

# __make_canvas_add_methods()
