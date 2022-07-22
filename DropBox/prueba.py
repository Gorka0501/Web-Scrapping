import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'f5ocn62l30x4qu0'
app_secret = 'xj2w9fm0oz2hipb'
server_addr = "localhost"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)

uri = "https://www.dropbox.com/oauth2/authorize"
cabeceras = {'Host': 'dropbox.com', 'client_id': app_key, 'redirect_uri': redirect_uri, 'response_type': 'code'}
cabeceras_econded = urllib.urlencode(cabeceras)
webbrowser.open(uri + "?" + cabeceras_econded)

codigo_auth = self.local_server()

print(codigo_auth)
self._root.destroy()

print(respuesta.url)
