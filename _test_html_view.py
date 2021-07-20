from distutils.version import LooseVersion
import wx
import wx.html2
import wx.lib.mixins.inspection
from application.define import APP_NAME, REQ_WX_VERSION_STRING


class WebViewPanel(wx.Panel):
    def __init__(self, parent, wx_id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, wx_id)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        self.mainSizer.Add(self.browser, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def show_html(self, html):
        self.browser.SetPage(html)

    def show_html_from_url(self, url):
        self.browser.LoadURL(url)

    def show_html_from_file(self, file_path):
        self.browser.LoadURL(wx.FileSystem.FileNameToURL(file_path))


class AppFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.webViewPanel = WebViewPanel(self)
        self.mainSizer.Add(self.webViewPanel, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()


class App(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        if LooseVersion(REQ_WX_VERSION_STRING) != LooseVersion(wx.VERSION_STRING):
            wx.MessageBox(caption="Warning",
                          message="You're using version %s of wxPython, but this copy of the demo was written for version %s.\n"
                                  "There may be some version incompatibilities..."
                                  % (wx.VERSION_STRING, REQ_WX_VERSION_STRING))

        self.InitInspection()  # for the InspectionMixin base class
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        self.SetAppName(APP_NAME)
        # Create and show the splash screen.  It will then create and
        # show the main frame when it is time to do so.  Normally when
        # using a SplashScreen you would create it, show it and then
        # continue on with the application's initialization, finally
        # creating and showing the main application window(s).  In
        # this case we have nothing else to do so we'll delay showing
        # the main frame until later (see ShowMain above) so the users
        # can see the SplashScreen effect.
        # _splash = GuiSplashScreen()
        # _splash.Show()
        _main_frm = AppFrame(None)
        _main_frm.Show()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
