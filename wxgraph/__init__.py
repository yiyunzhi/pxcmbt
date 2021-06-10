def _makeFloatCanvasAddMethods():  ## lrk's code for doing this in module __init__
    classnames = ["Circle", "Ellipse", "Arc", "Rectangle", "ScaledText", "Polygon",
                  "Line", "Text", "PointSet", "Point", "Arrow", "ArrowLine", "ScaledTextBox",
                  "SquarePoint", "Bitmap", "ScaledBitmap", "Spline", "Group"]
    for classname in classnames:
        klass = globals()[classname]

        def getaddshapemethod(klass=klass):
            def addshape(self, *args, **kwargs):
                Object = klass(*args, **kwargs)
                self.AddObject(Object)
                return Object

            return addshape

        addshapemethod = getaddshapemethod()
        methodname = "Add" + classname
        setattr(FloatCanvas, methodname, addshapemethod)
        docstring = "Creates %s and adds its reference to the canvas.\n" % classname
        docstring += "Argument protocol same as %s class" % classname
        if klass.__doc__:
            docstring += ", whose docstring is:\n%s" % klass.__doc__
        FloatCanvas.__dict__[methodname].__doc__ = docstring


_makeFloatCanvasAddMethods()