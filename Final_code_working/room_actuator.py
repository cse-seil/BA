from PIR import *
import sys
import MySQLdb as mdb
import csv
import time
from threading import Thread, Lock
import socket
from relay import *
import variable


def send_PIR():
  MESSAGE = "#" + data_id + "P,T;"#SIC205_R1_S01,T;"
  #variable.s.sendto(MESSAGE, (variable.ip_p1,variable.port_send_p1))
  while True:
    '''generate PIR code here'''
    variable.mutex.acquire()
    if variable.PIR_trigger and not variable.Light_State:
      #print "PIR-TRUE"
      #variable.s.sendall('PIR-TRUE')
      variable.s.sendto(MESSAGE, (variable.ip_p1,variable.port_send_p1))
      print "inside SeND PIR"
      variable.PIR_trigger = False
      variable.Light_State = True
      #t3.stop()
    variable.mutex.release()
      #time.sleep(5) #will need to remove this

def actuate():
  while True:
    print"waiting"
    data = variable.s_listen.recv(1024)
    print data
    #data = d[0]
    if data[0] =='#' and data[-1] == ';':
      col = data[1:-1].split(',')
      print col[0]
      print variable.data_id_couple
      if (col[0] == (data_id + "I")) or (col[0] == (data_id_couple + "I")):
        if col[1] == "HD":
          variable.mutex.acquire()
          variable.HD = True
          print variable.HD
          variable.mutex.release()

        if col[1] == "HND":
          variable.mutex.acquire()
          variable.HD = False
          print variable.HD
          variable.Cam_Standby = False
          variable.mutex.release()
 

if __name__ == '__main__' :

  variable.mutex = Lock()
  variable.HD = False
  with open('/home/pi/Final_code/config_rpi.cfg','r') as inf:
    fields = inf.readline()
    fields = inf.readline().replace('\n','')
    cols = fields.split(' ')
    port_recv_p2 = int(cols[1])# port which it listens on from proxy 2
    data_id = str(cols[0])
    if len(cols) == 3:
      variable.data_id_couple = str(cols[2]) # Changed after anshul
 
  con = mdb.connect("10.129.23.100" , "rohit" , "" , "BuildingAutomation")
  cur = con.cursor()
  cur.execute("select proxy_ip , proxy_listen_port  from proxy_info ;")
  row = cur.fetchone()
  variable.ip_p1 = str(row[0])
  variable.port_send_p1 = int(row[1]) 

  row = cur.fetchone()
  ip_p2 = str(row[0])
  port_send_cfg = int(row[1]) 
  con.close()
  ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
  #cfg_msg = "$add," + data_id + "I" +  "," + ip_own + "," + str(port_recv_p2) + ";"
  variable.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  #variable.s.sendto(cfg_msg,(ip_p2,port_send_cfg))

  variable.s_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  variable.s_listen.bind((ip_own,port_recv_p2))
  ''' Message to configure Proxy 2 '''
  print " connected"
  if(sys.argv[1] == str(0)):
    variable.automate = False
    print "here"
  if(sys.argv[1] == str(1)):
    variable.automate = True
    print "there"

  t1 = Thread(target = send_PIR)
  t1.start()
  t2 = Thread(target = actuate)
  t2.start()
  t3 = Thread(target = PIR)
  t3.start()
  t4 = Thread(target = relay_code)
  t4.start()
