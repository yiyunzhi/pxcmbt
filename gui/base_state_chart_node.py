from .define_gui import *


class StateChartNode:
    def __init__(self):
        self.shapeStyle = EnumShapeStyle.STYLE_DEFAULT
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self.isSelected = False

    def has_style(self, style):
        return (self.shapeStyle & style) != 0

    def add_style(self, style):
        self.shapeStyle |= style

    def get_connection_style(self):
        return self.connectionStyle

    def set_connection_style(self, style: EnumShapeConnectionStyle):
        self.connectionStyle = style
