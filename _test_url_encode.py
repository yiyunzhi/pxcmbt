import urllib.parse

params = {'suite': 'RajeevSingh',
          'case':'aa',
          'levent':'aa',
          'leventdata': ['+919999999999', '+628888888888']}
_encoded=urllib.parse.urlencode(params, doseq=True)
_decoded=urllib.parse.parse_qs(_encoded)
print(_encoded)
print(_decoded)