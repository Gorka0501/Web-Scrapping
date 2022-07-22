# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from bs4 import BeautifulSoup
import time
import helper


class eGela:
    _login = 0
    _cookie = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"
        #############################################
        cabeceras = {'Host': 'egela.ehu.eus'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        cabeceras_respuesta = respuesta.headers
        sesion = cabeceras_respuesta['Set-Cookie'].split(";")[0]

        cuerpo_respuesta = respuesta.content
        cuerpo_html = BeautifulSoup(cuerpo_respuesta, "html.parser")
        login_token = cuerpo_html.find_all('input', {'type': 'hidden'})
        login_token = str(login_token[0]).split('"')[5]
        #############################################

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 2. PETICION #####")
        #############################################
        metodo = 'POST'
        uri = "https://egela.ehu.eus/login/index.php"
        cabeceras = {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': sesion}
        contenido = {'logintoken': login_token,
                     'username': username.get(),
                     'password': password.get()}

        contenido_encoded = urllib.parse.urlencode(contenido)
        cabeceras['Content-Length'] = str(len(contenido_encoded))
        respuesta = requests.request(metodo, uri, data=contenido_encoded,
                                     headers=cabeceras, allow_redirects=False)

        cabeceras_respuesta = respuesta.headers
        print(respuesta.headers)
        if(cabeceras_respuesta['Location'] == 'https://egela.ehu.eus/login/index.php'):
            messagebox.showinfo("Alert Message", "Login incorrect!")
            return

        sesion_moodle = cabeceras_respuesta['Set-Cookie'].split(";")[0]
        location = cabeceras_respuesta['Location']
        #############################################

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")
        #############################################
        metodo = 'GET'
        url = location
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': sesion_moodle}
        respuesta = requests.request(metodo, url, headers=cabeceras, allow_redirects=False)

        cabeceras_respuesta = respuesta.headers
        location = cabeceras_respuesta['Location']
        #############################################

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        print("\n##### 4. PETICION #####")
        #############################################
        metodo = 'GET'
        url = location
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': sesion_moodle}
        respuesta = requests.request(metodo, url, headers=cabeceras, allow_redirects=False)

        cuerpo_respuesta = respuesta.content
        cuerpo_html = BeautifulSoup(cuerpo_respuesta, "html.parser")
        sis_web = cuerpo_html.find_all('div', {'class': 'info'})

        for asig in sis_web:
            nombre = asig.h3.a.text
            if nombre == "Sistemas Web":
                location = asig.find('a')['href']
        #############################################

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        if respuesta.status_code == 200:
            self.SWUri = location
            self._login = 1
            self._cookie = sesion_moodle
            self._root.destroy()

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        respuesta = requests.request(metodo, self.SWUri, headers=cabeceras, allow_redirects=False)

        cuerpo_respuesta = respuesta.content
        cuerpo_html = BeautifulSoup(cuerpo_respuesta, "html.parser")
        links = cuerpo_html.find_all('a', {'class': 'aalink'})

        cont = 0
        links_pdfs = []
        for link in links:
            if str(link.find('img')['src']).endswith('pdf'):
                links_pdfs.insert(cont, link.get('href'))
                cont += 1
        #############################################
        progress_step = float(100.0 / cont)

        print("\n##### Analisis del HTML... #####")
        #############################################
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        cont = 0
        for link in links_pdfs:
            respuesta = requests.request('GET', link, headers=cabeceras, allow_redirects=False)
            nombre = respuesta.headers['Location'].split("/")[-1]
            nombre = urllib.parse.unquote(nombre)
            self._refs.insert(cont, {'pdf_name': nombre, 'pdf_link': respuesta.headers['Location']})
            cont += 1
            progress = progress_step*cont
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        popup.destroy()
        #############################################

        # INICIALIZA Y ACTUALIZAR BARRA DE PROGRESO
        # POR CADA PDF ANIADIDO EN self._refs


        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        respuesta = requests.request('GET', self._refs[selection]['pdf_link'], headers=cabeceras, allow_redirects=False)
        pdf_name = self._refs[selection]['pdf_name']
        pdf_content = respuesta.content

        return pdf_name, pdf_content
