import wx


class HeaderPanel(wx.Panel):
    def __init__(self, title, sub_title, description='', parent=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.titleFont = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.subtitleFont = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.descriptionFont = wx.Font(8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.title = title
        self.subTitle = sub_title
        self.description = description
        self.ctrlTitle = wx.StaticText(self, wx.ID_ANY, self.title)
        self.ctrlTitle.SetFont(self.titleFont)
        self.ctrlSubTitle = wx.StaticText(self, wx.ID_ANY, self.subTitle)
        self.ctrlSubTitle.SetFont(self.subtitleFont)
        self.ctrlDesc = wx.StaticText(self, wx.ID_ANY, self.description)
        self.ctrlDesc.SetFont(self.descriptionFont)
        self.mainSizer.Add(self.ctrlTitle, 1, wx.EXPAND)
        self.mainSizer.Add(self.ctrlSubTitle, 1, wx.EXPAND)
        self.mainSizer.Add(self.ctrlDesc, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def set_title(self, title):
        self.title = title
        self.ctrlTitle.SetLabelText(title)

    def set_sub_title(self, text):
        self.subTitle = text
        self.ctrlSubTitle.SetLabelText(text)

    def set_description(self, text):
        self.description = text
        self.ctrlDesc.SetLabelText(text)
