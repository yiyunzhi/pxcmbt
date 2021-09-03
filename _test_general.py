import urllib.parse

_param={'a':12,'v':12.44,'c':'dwafw','c2':32424}
_url='?'+urllib.parse.urlencode(_param, doseq=True)
_query=urllib.parse.urlsplit(_url).query
print(_url)
print(_query)
print(urllib.parse.parse_qs(_query))