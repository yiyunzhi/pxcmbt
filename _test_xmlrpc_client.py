import time
import xmlrpc.client

_proxy = xmlrpc.client.ServerProxy("http://localhost:8180/", allow_none=True)

while True:
    _next = _proxy.next()
    if _next == '__END__':
        print('----END----')
        break
    print('-' * 30 + 'run test step %s/%s' % (_next.get('seqID'), _next.get('stepTotal')) + '-' * 30)
    print("test_step_case: %s" % _next.get('case'))
    print("test_step_feature: %s" % _next.get('feature'))
    print("test_step_desc: %s" % _next.get('stepDesc'))
    print("test_step_resolved: %s" % _next.get('resolved'))
    print("test_step_fEnterEvent: %s" % _next.get('fEnterEvent'))
    print("test_step_fExitEvent: %s" % _next.get('fExitEvent'))
    print("test_step_devEnterEvent: %s" % _next.get('devEnterEvent'))
    print("test_step_devExitEvent: %s" % _next.get('devExitEvent'))
    print("test_step_OBOs: %s" % _next.get('obos'))
    time.sleep(0.5)
    print('test done, set state:', 1)
    _proxy.set_state(1)
    time.sleep(0.8)
    print('test done, set state:', 2)
    _proxy.set_state(2)
