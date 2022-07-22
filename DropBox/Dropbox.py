import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'cnpqvg1z8x9uxsc'
app_secret = 'xj2w9fm0oz2hipb'
server_addr = "localhost"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)


class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # por el puerto 8090 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccio 302 del navegador
        client_connection, client_address = server_socket.accept()
        eskaera = str(client_connection.recv(1024))
        print("\tRequest from the browser received at local server:")
        print(eskaera)

        # buscar en solicitud el "auth_code"
        lehenengo_lerroa = eskaera.split('\n')[0]
        aux_auth_code = lehenengo_lerroa.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode())
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        #############################################

        uri = "https://www.dropbox.com/oauth2/authorize"
        cabeceras = {'Host': 'dropbox.com', 'client_id': app_key, 'redirect_uri': redirect_uri, 'response_type': 'code'}
        cabeceras_econded = urllib.parse.urlencode(cabeceras)
        webbrowser.open(uri + "?" + cabeceras_econded)

        codigo_auth = self.local_server()

        metodo = "Post"
        uri = "https://api.dropboxapi.com/oauth2/token"
        cabeceras = {'Host': 'api.dropboxapi.com', 'Content-Type': 'application/x-www-form-urlencoded'}
        datos = {'code': codigo_auth, 'client_id': app_key, 'client_secret': app_secret, 'redirect_uri': redirect_uri,
                 'grant_type': 'authorization_code'}
        respuesta = requests.request(metodo, uri, headers=cabeceras,data=datos, allow_redirects=False)

        contenido = respuesta.text
        cJson = json.loads(contenido)
        print(cJson)
        self._access_token = str(cJson['access_token'])
        print(self._access_token)
        self._root.destroy()

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = 'https://api.dropboxapi.com/2/files/list_folder'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-list_folder
        #############################################
        if self._path == "/":
            path = ""
        else:
            path = self._path

        metodo = "Post"
        cabeceras = {'Host': 'api.dropboxapi.com','Authorization': 'Bearer ' + self._access_token, 'Content-Type': 'application/json'}
        datos = {'path': path}
        jDatos = json.dumps(datos)
        respuesta = requests.request(metodo, uri, headers=cabeceras , data=jDatos, allow_redirects=False)
        #############################################
        contenido = respuesta.text
        contenido_json = json.loads(contenido)
        self._files = helper.update_listbox2(msg_listbox, self._path, contenido_json)

    def transfer_file(self, file_path, file_data):
        print("/upload")
        uri = 'https://content.dropboxapi.com/2/files/upload'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        #############################################
        metodo = "Post"
        datos = {'path': file_path, 'mode': 'add', 'autorename': True, 'mute': False}
        jDatos = json.dumps(datos)
        cabeceras = {'Host': 'content.dropboxapi.com', 'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/octet-stream', 'Dropbox-API-Arg': jDatos}

        respuesta = requests.request(metodo, uri, headers=cabeceras, data=file_data, allow_redirects=False)
        contenido = respuesta.text
        print(respuesta.status_code)
        print(contenido)
        #############################################

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-delete
        #############################################
        metodo = "Post"
        cabeceras = {'Host': 'api.dropboxapi.com', 'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json' }
        datos = {'path' : file_path }
        jDatos = json.dumps(datos)
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=jDatos, allow_redirects=False)
        contenido = respuesta.text
        print(respuesta.status_code)
        print(contenido)
        #############################################

    def create_folder(self, path):
        print("/create_folder")
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-create_folder
        #############################################
        metodo = "Post"
        cabeceras = {'Host': 'api.dropboxapi.com', 'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        datos = {'path': path, 'autorename': True}
        jDatos = json.dumps(datos)
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=jDatos, allow_redirects=False)
        contenido = respuesta.text
        print(respuesta.status_code)
        print(contenido)
        self._root.destroy()
        #############################################
