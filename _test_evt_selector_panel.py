import wx
from gui.panel_event_selector import EventSelectorPanel
from application.class_mbt_event import MBTEventManager, MBTEvent, MBTEventData

evt_a_data = [{'name':'dataA','dataType': 'integer'},{'name':'dataB','dataType': 'integer'},{'name':'dataC','dataType': 'integer'}]
evt_b_data = [{'name':'dataA','dataType': 'integer'},{'name':'dataC','dataType': 'integer'}]
evt_c_data = [{'name':'dataA','dataType': 'integer'},{'name':'dataB','dataType': 'integer'}]
evt_a = MBTEvent(name='A', data=evt_a_data)
evt_b = MBTEvent(name='B', data=evt_b_data)
evt_c = MBTEvent(name='C', data=evt_c_data)
evtmgr = MBTEventManager()
evtmgr.register_event(evt_a)
evtmgr.register_event(evt_b)
evtmgr.register_event(evt_c)
if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, size=(720, 680), title='Simple application')
    panel = EventSelectorPanel(evtmgr, parent=frame)
    _dummy_events = [('A', '0x0102,0x0202,0x000'), ('B', '0x0103,0x0202,0x000'),
                     ('C', '0x0104,0x0202,0x000')]
    panel.set_selected_events(_dummy_events)
    frame.Show()
    app.MainLoop()
