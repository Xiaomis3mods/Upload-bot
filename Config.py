import os

class Config(object):
      def __init__(self):
          self.BotToken     = '2107581509:AAHDLAgjLTo8SEGnBqlcmhxVA80SOCEl2Qc'
          self.ChunkSize    = 80
          self.ChunkSizeTel = 1000
          self.ChunkFixed   = 150
          self.FileLimit    = 1024 * 1024 * 400
          self.ExcludeFiles = ['MoodleApp.pyproj','bot.py','Config.py','multiFile.py','MoodleUhoClient.py','S5Crypto.py','S4Crypto.py','nuvidb.txt','requirements.txt','Procfile','__pycache__','.git','.profile.d','.heroku','bot.session','bot.session-journal','output','.cache']
          self.ChunkedFileLimit = 1024 * 1024 * 1024
          self.InProcces = False
          self.BotChannel = '-1001432878672'
          self.AdminUsers = ['Harold780']
          self.current_user_msg = ''
          self.current_chanel_msg = ''
          self.procesing = False
          self.watching = False
          self.watch_message = []
          self.moodleUser = 'livanp'
          self.moodlepassword = 'Copernico*2'
          self.users = []
          self.userindex = 0
          self.nuvContent = ''
          self.msgurls = ''


      def setS3Token(self,token : str):
          self.S3Token = token

      def setBotToken(self,token : str):
          self.BotToken = token

      def setChunkSize(self,chunk : int):
          self.ChunkSize = chunk

      def setChunkSizeTel(self,chunk : int):
          self.ChunkSizeTel = chunk

      def setAccount(self,user='',passw=''):
          self.moodleUser = user
          self.moodlepassword =  passw

      def toStr(self):
          return '[Chunk Size]\n' + str(self.ChunkSize) + '\n\n[ChunkSizeTel]\n' + str(self.ChunkSizeTel)
      

      #Cosas de los Usuarios
      def stepUser(self):
          self.userindex += 1
          if self.isAvailableNub() == False:
              return False
          self.moodleUser = self.users[self.userindex]['user']
          self.moodlepassword = self.users[self.userindex]['passw']
          return True

      def stepUserZero(self):
          self.userindex = 0
          self.moodleUser = self.users[self.userindex]['user']
          self.moodlepassword = self.users[self.userindex]['passw']

      def isAvailableNub(self):
          if self.userindex >= len(self.users):
              return False
          return True
