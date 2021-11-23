import requests
import os
import textwrap
import re
import json

from bs4 import BeautifulSoup

class MoodleClient(object):
    def __init__(self, user,passw):
        self.username = user
        self.password = passw
        self.session = requests.Session()

    def getsession(self):
        return self.session    

    def login(self):
        login = 'https://evea.uh.cu/login/index.php'
        resp = self.session.get(login)
        cookie = resp.cookies.get_dict()
        soup = BeautifulSoup(resp.text,'html.parser')
        anchor = soup.find('input',attrs={'name':'anchor'})['value']
        logintoken = soup.find('input',attrs={'name':'logintoken'})['value']
        username = self.username
        password = self.password
        payload = {'anchor': '', 'logintoken': logintoken,'username': username, 'password': password, 'rememberusername': 1}
        loginurl = 'https://evea.uh.cu/login/index.php'
        resp2 = self.session.post(loginurl, data=payload)
        counter = 0
        for i in resp2.text.splitlines():
            if "loginerrors" in i or (0 < counter <= 3):
                counter += 1
                print(i)
        if counter>0:
            print('No pude iniciar sesion')
            return False
        else:
            print('E iniciado sesion con exito')
            return True

    def upload_file(self,file,saved = True):
        fileurl = 'https://evea.uh.cu/user/files.php'
        resp = self.session.get(fileurl)
        print('Resp: '+str(resp))
        soup = BeautifulSoup(resp.text,'html.parser')
        sesskey  =  soup.find('input',attrs={'name':'sesskey'})['value']
        print('Sesskey: '+str(sesskey))
        _qf__user_files_form = soup.find('input',attrs={'name':'_qf__user_files_form'})['value']
        print('_qf__user_files_form: '+str(_qf__user_files_form))
        files_filemanager = soup.find('input',attrs={'name':'files_filemanager'})['value']
        print('files_filemanager: '+str(files_filemanager))
        returnurl = soup.find('input',attrs={'name':'returnurl'})['value']
        print('Returnurl: '+str(returnurl))
        submitbutton = soup.find('input',attrs={'name':'submitbutton'})['value']
        print('Submitbutton: '+str(submitbutton))
        #usertext =  soup.find('span',attrs={'class':'usertext mr-1'}).contents[0]
        #print('Usertext: '+str(usertext))
        query = self.extractQuery(soup.find('object',attrs={'type':'text/html'})['data'])
        print('Query: '+str(query))
        client_id = self.getclientid(resp.text)
        print('Client_id: '+str(client_id))
        of = open(file,'rb')
        upload_file = {
            'repo_upload_file':(file,of,'application/octet-stream'),
            }
        upload_data = {
            'title':(None,''),
            'author':(None,'Livan'),
            'license':(None,'allrightsreserved'),
            'itemid':(None,query['itemid']),
            'repo_id':(None,4),
            'p':(None,''),
            'page':(None,''),
            'env':(None,query['env']),
            'sesskey':(None,sesskey),
            'client_id':(None,client_id),
            'maxbytes':(None,query['maxbytes']),
            'areamaxbytes':(None,query['areamaxbytes']),
            'ctx_id':(None,query['ctx_id']),
            'savepath':(None,'/')}
        post_file_url = 'https://evea.uh.cu/repository/repository_ajax.php?action=upload'
        resp2 = self.session.post(post_file_url, files=upload_file,data=upload_data)
        of.close()
        data = self.parsejson(resp2.text)
        payload = {
            'returnurl':fileurl,
            'sesskey':sesskey,
            '_qf__user_files_form':_qf__user_files_form,
            'files_filemanager':files_filemanager,
            'cancel':'Cancelar'
           # 'submitbutton':'Guardar+cambios'
        }
        return data

    def parsejson(self,json):
        data = {}
        tokens = str(json).replace('{','').replace('}','').split(',')
        for t in tokens:
            split = str(t).split(':',1)
            data[str(split[0]).replace('"','')] = str(split[1]).replace('"','')
        return data

    def getclientid(self,html):
        index = str(html).index('client_id')
        max = 25
        ret = html[index:(index+max)]
        return str(ret).replace('client_id":"','')

    def extractQuery(self,url):
        tokens = str(url).split('?')[1].split('&')
        retQuery = {}
        for q in tokens:
            qspl = q.split('=')
            retQuery[qspl[0]] = qspl[1]
        return retQuery
    
