from telethon import TelegramClient, events, sync
import asyncio
import base64
from MoodleClient import MoodleClient
from Config import Config
import multiFile
import zipfile
from zipfile import ZipFile
import os
import requests
import re
import random
import time

conf = Config()

bot_token = '1956937895:AAGqh1Tt2MKezu2JslHD3QmfFLcjIi0uR_4'
api_id = '7373129'
api_hash = 'f2537822420e8dfc308c6b3e41989366'


async def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = '(' + str(porcent) + '% '
		index_make = 1
		make_text += '100%)'
		make_text += '\n['
		while(index_make<21):
			  if porcent >= index_make * 5: make_text+='█'
			  else: make_text+='░'
			  index_make+=1
		make_text += ']\n'
		make_text += '(' + str(index) + '/' + str(max) + ')'
		return make_text
	except Exception as ex:
			return ''
async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_name(file):
    return str(file).split('.')[0]

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/');
            return tokens[len(tokens)-1]
    except:
           tokens = str(url).split('/');
           return tokens[len(tokens)-1]
    return ''

def fixed_name(name):
    return str(name).replace('%20',' ')

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))

async def down_chunked_fixed(url,bot,ev,msg):
    try:
        multiFile.clear()
        conf.Subido = 0
        msgurls = ''
        maxsize = 1024 * 1024 * 1024 * 2
        req = requests.get(url, stream = True,allow_redirects=True)
        file_size = req_file_size(req)
        chunk_size = 1024 * 1024 * conf.ChunkSize
        if req.status_code == 200:
            file_name = get_url_file_name(url,req)
            file_name = file_name.replace('"',"")
            file_name = fixed_name(file_name)

            await msg.edit('Preparando para descargar...\n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            iterator = 1
            file_wr = open(file_name,'wb')
            print('Descargando...')
            chunk_por = 0
            chunkrandom = random.randint(10.00,20.00)
            inicio = time.time()
            total = file_size
            for chunk in req.iter_content(chunk_size = 1024 * 1024 * chunkrandom):
                chunk_por += len(chunk)
                porcent = round(float(chunk_por / total * 100), 2)
                make_text = str(porcent) + '% / 100%'
                index_make = 1
                make_text += '\n['
                while(index_make<21):
                    if porcent >= index_make * 5:
                        make_text+='█'
                    else: 
                        make_text+='░'
                    index_make+=1
                make_text += ']'
                await msg.edit('Descargando '+str(file_name)+'...\nProgreso:\n'+str(make_text)+'\nDescargado: '+str(round(float(chunk_por) / 1024 / 1024, 2))+' MB\nTotal: ' +str(round(total / 1024 / 1024, 2))+ ' MB')
                file_wr.write(chunk)
            file_wr.close()

            if file_size > chunk_size: 
                await msg.edit('🖇Comprimiendo📦 \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))
                mult_file =  multiFile.MultiFile(file_name+'.7z',chunk_size)
                zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
                zip.write(file_name)
                zip.close()
                mult_file.close()
                index = 1
                await msg.edit('Preparando para subir...')
                for f in multiFile.files:
                    comienzo = time.time()
                    fsize = await get_file_size(f)
                   # await msg.edit('Subiendo a Telegram \n' +str(f)+ '' +str(sizeof_fmt(fsize)))
                   # await bot.send_file(ev.message.chat,f)
                    progres  = await text_progres(index,len(multiFile.files))
                    moodle = MoodleClient(conf.moodleUser,conf.moodlepassword)
                    loged = moodle.login()
                    if loged == True:
                        resp = moodle.upload_file(f)
                        final = time.time()
                        conf.Subido += conf.ChunkSize 
                        tiempo = round(float(final-comienzo), 2)
                        speed = round(float(fsize / tiempo) / 1024 / 1024, 2)
                        await msg.edit('Subiendo ' + str(f) + ' '+ str(sizeof_fmt(fsize))+ ' ...\n'  + str(progres) + '\nVelocidad: '+str(speed)+ ' Mb/s\nSubido: '+str(sizeof_fmt(conf.Subido)))
                        if 'url' in resp:
                            msgurls += '\n' + f + ':' + '\n' + str(resp['url']).replace('\\','').replace('//','').replace(':','://') + '\n'
                        else:
                            msgurls += '\n' + f + ': ' + data[0] + '\n'
                        os.unlink(f)
                    index+=1
                os.unlink(file_name)
            else:
                  await msg.edit('📤Subiendo📤 \n ' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))
                  moodle = MoodleClient(conf.moodleUser,conf.moodlepassword)
                  loged = moodle.login()
                  if loged == True:
                      resp = moodle.upload_file(file_name)
                      if 'url' in resp:
                          msgurls += '\n' + file_name + ':' + '\n' + str(resp['url']).replace('\\','').replace('//','').replace(':','://') + '\n'
                      else:
                          msgurls += '\n' + file_name + ': ' + data[0] + '\n'
                  os.unlink(file_name)
            await msg.edit('Proceso Finalizado!!')
            txtfile = open(file_name+'.txt','w')
            txtfile.write(msgurls)
            txtfile.close()
            txtfile = open(file_name+'.txt','rb')
            await bot.send_file(ev.message.chat,txtfile)
            txtfile.close()
            os.unlink(file_name+'.txt')
            await bot.send_message(ev.chat_id, '✅Subido a aulacened.uci.cu a la cuenta de ' + str(conf.moodleUser)+'|'+str(conf.moodlepassword))
    except Exception as e:
            await msg.edit('(Error Subida) - ' + str(e))

async def down_to_tel(url,bot,ev,msg):
    try:
         multiFile.files.clear()
         txt_list = {}
         req = requests.get(url, stream = True,allow_redirects=True)
         if req.status_code == 200:
            file_size = req_file_size(req)
            file_name = get_url_file_name(url,req)
            file_name = file_name.replace('"',"")
            file_name = fixed_name(file_name)

            await msg.edit('📥Descargando📥 \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            file_wr = open(file_name,'wb')
            print('Descargando...')
            for chunk in req.iter_content(chunk_size = 1024 * 1024 * conf.ChunkFixed):
                    if chunk:
                        file_wr.write(chunk)
            file_wr.close()

            await msg.edit('🖇Comprimiendo📦 \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            mult_file =  multiFile.MultiFile(get_name(file_name)+'.7z',1024 * 1024 * conf.ChunkSizeTel)
            zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(file_name)
            zip.close()
            mult_file.close()
            os.unlink(file_name)

            for f in multiFile.files:
                 f_size = await get_file_size(f)
                 await msg.edit('📤Subiendo a Telegram✈ \n' + str(f) + '\n' + str(sizeof_fmt(f_size)))
                 await bot.send_file(ev.message.chat,f)
                 os.unlink(f)
    except Exception as e:
            await msg.edit('(down_chunked) ' + str(e))
            print(str(e))
    await msg.edit('📌Proceso Finalizado❗')

async def process_message(text,bot,ev,msg):
    if '/dtel' in text:
        await down_to_tel(text.replace('/dtel ',''),bot,ev,msg)
    elif 'http' in text:
        await down_chunked_fixed(text,bot,ev,msg)
    elif '/account' in text:
        try:
            account = text.replace('/account ','').split(',')
            conf.setAccount(account[0],account[1])
            moodle = MoodleClient(conf.moodleUser,conf.moodlepassword)
            loged = moodle.login()
            if loged == True:
                await msg.edit('✅Has Configurado la cuenta ' + str(conf.moodleUser)+ ' al Bot✅')
            else:
                 await msg.edit('🚫Error en la Cuenta Revise Sus Credenciales🚫')
        except Exception as ex:
             await msg.edit(str(ex))
    elif '/sc ' in text:
        conf.setChunkSize(int(text.replace('/sc ','')))
        await msg.edit('🖇El tamaño zip al subir a la nube☁ a Cambiado✂️')
    elif '/sct ' in text:
        conf.setChunkSizeTel(int(text.replace('/sct ','')))
        await msg.edit('🖇El Tamaño de los zip al subir a Telegram ha cambiado✈')
    elif '/help' in text:
        await msg.edit('Comandos disponibles😄')
        await bot.send_message(ev.chat_id, '👉Para subir archivos a telegram desde un enlace de descarga usa /dtel😁👌\nPara cambiar el tamaño de esos archivos usas /sct')
        await bot.send_message(ev.chat_id, '❓Ejemplo /dtel https://enlace/de/descarga✅\n❓Ejemplo: /sct 1800✅')
        await bot.send_message(ev.chat_id, '👉Para subir archivos a la nube☁ desde un enlace de descarga usa /dtd😁👌')
        await bot.send_message(ev.chat_id, '❓Ejemplo /dtd https://enlace/de/descarga✅')
        await bot.send_message(ev.chat_id, '👉Para saber el tamaño de los archivos zip y a q cuenta se está subiendo escriba solo /gc👌')
    elif '/gc' in text:
        await msg.edit('💥El Tamaño de Los zip al subir a la nube es:\n👇👇\n' + str(conf.ChunkSize) + 'MB\n⚡El tamaño al subir a telegram es\n👇👇\n' + str(conf.ChunkSizeTel) + 'MB\n✅La cuenta configurada es:\n👇👇\n' +str(conf.moodleUser))
    elif '/acc ' in text:
        conf.AdminUsers.append(text.replace('/acc ',''))
        await msg.edit('Le a dado Acceso a ' + text.replace('/acc ',''))
    elif '/ban ' in text:
        if text.replace('/ban ','') in conf.AdminUsers and text.replace('/ban ','') != conf.AdminUsers[0]:
            conf.AdminUsers.remove(text.replace('/ban ',''))
            await msg.edit('El Usuario ' + text.replace('/ban ','') + ' A Sido Baneado')
        else:
            await msg.edit('Ese Usuario es Fantasma!')
    else:
        await msg.edit('No puedo procesar esto😔')
    pass


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))


async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size

def get_full_file_name(file):
    tokens = file.split('.')
    name = ''
    index = 0
    for t in tokens:
        if index < len(tokens):
            name += t + '.'
        index += 1
    return name


async def process_txt(file,bot,ev,msg):
    try:
        await msg.edit('Leyendo archivos...🔄')
        multiFile.files.clear()
        f = open(file,'r')
        txt = f.read()
        f.close()
        links = str(txt).split('\n')
        files = []
        baseName = ''
        for l in links:
            if l == '':continue
            tokens = str(l).split('\t')
            baseName = tokens[1]
            url = tokens[0]
            saveFile = download(url,baseName,bot,ev,msg)
            files.append(saveFile)
        if len(file) > 0:
            await msg.edit('🖇Comprimiendo...✂️')
            mult_file =  multiFile.MultiFile(get_name(baseName)+'.7z',1024 * 1024 * conf.ChunkSize)
            with zipfile.ZipFile(mult_file,  mode='w') as zip:
                 for f in files:
                     zip.write(f)
                     os.unlink(f)
            mult_file.close()
            for f in multiFile.files:
                     f_size = await get_file_size(f)
                     await bot.send_message(ev.chat_id,'Subiendo a Telegram \n' + str(f) + '\n' + str(sizeof_fmt(f_size)))
                     await bot.send_file(ev.message.chat,f)
        pass
    except Exception as h:
        await msg.edit('Error\n' +str(h))

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
           print(str(e))


async def process_file(file,bot,ev,msg):
    try:
        multiFile.clear()
        conf.Subido = 0
        msgurls = ''
        maxsize = 1024 * 1024 * 1024 * 2
        file_size = await get_file_size(file)
        chunk_size = 1024 * 1024 * conf.ChunkSize

        if file_size > chunk_size:
            await msg.edit('🖇Comprimiendo📦 \n' + str(file) + '\n' + str(sizeof_fmt(file_size)))
            mult_file =  multiFile.MultiFile(file + '.7z',chunk_size)
            zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(file)
            zip.close()
            mult_file.close()
            index = 0
            for f in multiFile.files:
                comienzo = time.time()
                f_size = await get_file_size(f)
               # await msg.edit('Subiendo a Telegram \n' +str(f)+ '' +str(sizeof_fmt(f_size)))
               # await bot.send_file(ev.message.chat,f)
                progres  = await text_progres(index,len(multiFile.files))
                await msg.edit('Preparando para subir...')
                moodle = MoodleClient(conf.moodleUser,conf.moodlepassword)
                loged = moodle.login()
                if loged == True:
                    resp = moodle.upload_file(f)
                    final = time.time()
                    conf.Subido += f_size
                    tiempo = round(float(final-comienzo), 0)
                    speed = round(float(f_size / tiempo) / 1024 / 1024, 2)
                    await msg.edit('Subiendo ' + str(f) + ' '+ str(sizeof_fmt(f_size))+ ' ...\n'  + str(progrestext) + '\nVelocidad: '+str(speed)+ ' Mb/s\nSubido: '+str(sizeof_fmt(conf.Subido)))
                    if 'url' in resp:
                        msgurls += '\n' + f + ':' + '\n' + str(resp['url']).replace('\\','').replace('//','').replace(':','://') + '\n'
                    else:
                        msgurls += '\n' + f + ': ' + data[0] + '\n'
                    os.unlink(f)
                index+=1
            os.unlink(file)
        else:
            await msg.edit('📤Subiendo📤 \n ' + str(file) + '\n' + str(sizeof_fmt(file_size)))
            moodle = MoodleClient(conf.moodleUser,conf.moodlepassword)
            loged = moodle.login()
            if loged == True:
                resp = moodle.upload_file(file)
                if 'url' in resp:
                    msgurls += '\n' + file + ':' + '\n' + str(resp['url']).replace('\\','').replace('//','').replace(':','://') + '\n'
                else:
                    msgurls += '\n' + file + ': ' + data[0] + '\n'
                os.unlink(file)
        await msg.edit('Proceso Finalizado!!')
        txtfile = open(file+'.txt','w')
        txtfile.write(msgurls)
        txtfile.close()
        txtfile = open(file+'.txt','rb')
        await bot.send_file(ev.message.chat,txtfile)
        txtfile.close()
        os.unlink(file+'.txt')
        await bot.send_message(ev.chat_id, '😁Archivos subidos a '+str(conf.moodleUser)+'|'+str(conf.moodlepassword))
    except Exception as e:
            await msg.edit(str(e))


def is_accesible(user):
    return user in conf.AdminUsers


async def processMy(ev,bot):
    try:
        if is_accesible(ev.message.chat.username):
                        if conf.procesing == False:
                            #clear_cache()
                            text = ev.message.text
                            conf.procesing = True
                            message = await bot.send_message(ev.chat_id, 'Procesando...🔄')
                            if ev.message.file:
                                await message.edit('📥Archivo Econtrado Descargando...📥')
                                file_name = await bot.download_media(ev.message)
                                if '.txt' in file_name:
                                   await process_txt(file_name,bot,ev,message)
                                else:
                                   await process_file(file_name,bot,ev,message)
                            elif text:
                                await process_message(text,bot,ev,message)
                            conf.procesing = False
                        else:
                            await bot.send_message(ev.chat_id,'Estoy trabajando Por favorEspere...⏳')
    except Exception as e:
                        await bot.send_message(str(e))
                        conf.procesing = False


def init():
    try:
        bot = TelegramClient( 
            'bot', api_id=api_id, api_hash=api_hash).start(bot_token=bot_token) 

        bot.send_message(1117027193, 'Bot Activo😎!!')
        action = 0
        actual_file = ''

        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
                text = ev.message.text
                clear_cache()
                if '#watch' in text:
                    await bot.send_message(ev.chat_id,'Esperando...')
                    conf.watching = True
                elif '#start' in text:
                    conf.watching = False
                    await bot.send_message(ev.chat_id,'Proceso Iniciado!')
                    for e in conf.watch_message:
                      await processMy(e,bot)
                    conf.watch_message.clear()
                elif conf.watching==True:
                    conf.watch_message.append(ev)
                elif '#stop' in text:
                      watching = False
                      watch_message.clear()
                elif conf.watching==False:
                      await processMy(ev,bot)


        loop = asyncio.get_event_loop() 
        loop.run_forever()
    except:
        init()
        conf.procesing = False

if __name__ == '__main__': 
   init()
