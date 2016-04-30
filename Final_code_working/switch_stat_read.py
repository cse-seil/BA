import MySQLdb as mdb
import glob
import serial
import socket
#ser = serial.Serial(uC_USBPort, baudrate, timeout = 0.01)
def switch_stat_read():
  con = mdb.connect("10.129.23.100" , "rohit" , "" , "BuildingAutomation")
  cur = con.cursor()
  cur.execute("select proxy_ip , proxy_listen_port  from proxy_info ;")
  row = cur.fetchone()
  ip_p1 = str(row[0])
  port_send_p1 = int(row[1]) 
  con.close()
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  arduPort = glob.glob("/dev/ttyACM*")
  if len(arduPort) > 0:
    print "Connected to serial port"
    ser = serial.Serial(arduPort[0], baudrate=115200, timeout = 0.1 , parity=serial.PARITY_EVEN,rtscts=1)
  else:
    print "NO serial port found"
    exit(1)
  stat = ser.readline()
  while True:
    if len(stat) > 0:
      stat = stat.replace('\n','')
      stat = stat.replace('\r','')
      sock.sendto(stat,(ip_p1,port_send_p1))
      #print stat
    #else:
    #  print "nothing"
    stat = ser.readline()

if __name__ == "__main__":
  switch_stat_read()
