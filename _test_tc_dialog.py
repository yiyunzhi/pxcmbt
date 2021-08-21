import wx
from gui.dialog_tc import TCDialog
from application.class_mbt_event import MBTEventManager, MBTEvent, MBTEventData

_tcs = ['ADWAHUWHFUAIHFUIWAHIFHWUAIHFUWIAHUIFWHAUIHFUIWAHUFIWHAUIFHUIWAHFUIWAHUIFHWUIAHFUIWHAUIFHWUAIHFUIW', 'V', 'C']
if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, size=(720, 680), title='Simple application')
    panel = TCDialog(_tcs, frame)
    frame.Show()
    panel.ShowModal()
    app.MainLoop()
