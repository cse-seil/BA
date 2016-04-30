#!/usr/bin/python
# Measure the holding time of a PIR module
import serial
import time
import RPi.GPIO as GPIO
import glob
import variable
import socket
from threading import Lock
#print PIR_trigger
#uC_USBPort = '/dev/ttyACM0'
'''
baudrate = 9600
arduPort = glob.glob("/dev/ttyACM*")
if len(arduPort) > 0:
  print "Connected to serial port"
  ser = serial.Serial(arduPort[0], baudrate=9600, timeout = 0.01)
else:
  print "NO serial port found"
  exit(1)

#ser = serial.Serial(uC_USBPort, baudrate, timeout = 0.01)

def myread():
#serialMsg = ser.read(2)     #reads 2 bytes and removes it out of the buffer
  if ser.read(2) == 'S_' :     #checking for valid message
    variable.switchStatus = ser.read(8) #read the next 8 bytes sent from arduino, 9th and 10th byte are /r/n  
    print variable.switchStatus
'''
  
def PIR():
  # Use BCM GPIO references instead of physical pin numbers
  global PIR_trigger
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  # Define GPIO to use on Pi
  GPIO_PIR = 12 # PIR input pin

  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  except socket.error:
    print 'Failed to create socket'
    sys.exit()

  #host = '10.129.23.161'
  #port = 5010
  host = variable.ip_p1
  port = variable.port_send_p1

  # BCM Pin definiting 
  GPIO_L1 = 6 # relay1 output pin
  GPIO_L2 = 13
  GPIO_L3 = 19
  GPIO_L4 = 26
  GPIO_L5 = 23
  #GPIO_relay2 = 16 # relay2

  print "PIR Module Holding Time Test (CTRL-C to exit)"
   
  # Set PIR pin as input
  GPIO.setup(GPIO_PIR,GPIO.IN)   
  # set relay1 gpio pin as output, with initial state = 0 
  if(variable.automate):
    GPIO.setup(GPIO_L1, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_L2, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_L3, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_L4, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_L5, GPIO.OUT, initial=0)
    variable.mutex.acquire()
    variable.Light_State = False
    variable.mutex.release()

  #GPIO.setup(GPIO_relay2, GPIO.OUT, initial=0)
  if(not variable.automate):
    GPIO.setup(GPIO_L1, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_L2, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_L3, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_L4, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_L5, GPIO.OUT, initial=1)
  relay_off_delay = 10 #time for auto-off of appliance
  Current_State = 0 
  Previous_State = 0
  start_time = 0
  stop_time = 0

  try:
   
    print "Waiting for PIR to settle ..."
   
    fp = open("/home/pi/Final_code/state_status.csv","a")
    # Loop until PIR output is 0
    while GPIO.input(GPIO_PIR)==1:
      Current_State  = 0
   
    print "  Ready"
    
    with open('/home/pi/Final_code/config_rpi.cfg','r') as inf:
      fields = inf.readline()
      fields = inf.readline().replace('\n','')
      cols = fields.split(' ')
      room = str(cols[0])# data_id

    with open("/home/pi/Final_code/config_param_rpi.cfg","r") as inf:
      t = inf.readline() # ignore first line
      field = inf.readline().split(" ")
      ulimit = float(field[0])
      llimit = float(field[1])
      flimit = float(field[2].replace("\n",""))
    
    
    Timer = time.time()
    # Loop until users quits with CTRL-C
    while True :
      #myread()
      # Read PIR state
      Current_State = GPIO.input(GPIO_PIR)
      variable.mutex.acquire()
      
      if(variable.HD and (time.time() - Timer > 10)):
        Timer = time.time()
        ''' Log here '''
        msg = '#' + room + "," + str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + (str(variable.Temp)) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + ',' + str(variable.automate) + ';'
        s.sendto(msg, (host, port))

        fp.write(str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + str(variable.Temp) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + '\n')
        fp.flush()
      if(not variable.HD and (time.time() - Timer > 60)):
        Timer = time.time()
        ''' Log here '''
        msg = '#' + room + "," + str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + (str(variable.Temp)) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + ',' + str(variable.automate) + ';'
        s.sendto(msg, (host, port))
        fp.write(str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + str(variable.Temp) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + '\n')
        fp.flush()
     
      if Current_State==1 and not variable.Light_State:
        # PIR is triggered
        start_time=time.time()  # update start time
        variable.PIR_trigger = True
        variable.Cam_Standby = True
        ''' Log here '''
        msg = '#' + room + "," + str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + (str(variable.Temp)) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + ',' + str(variable.automate) + ';'
        s.sendto(msg, (host, port))
        fp.write(str(variable.PIR_trigger) + "," + str(variable.HD) + "," + str(variable.Cam_Standby) + ',' + str(variable.Light_State) + ',' + str(variable.Fan_State) + ',' + str(variable.AC_State) + ',' + str(variable.Temp) + ',' +(str(ulimit))+',' + (str(llimit))+ ',' + (str(flimit)) + ',' + str(variable.switchStatus) + '\n')
        fp.flush()
        #print " In Other",variable.PIR_trigger
        #print "  Motion detected!"
        # set relay
        if(variable.automate):
          GPIO.output(GPIO_L1,GPIO.HIGH)
          GPIO.output(GPIO_L2,GPIO.HIGH)
          GPIO.output(GPIO_L3,GPIO.HIGH)
          GPIO.output(GPIO_L4,GPIO.HIGH)
          GPIO.output(GPIO_L5,GPIO.HIGH)
          #variable.Light_State = True # dont put light state here as it is being checked in room actuator thread
        #GPIO.output(GPIO_relay2,GPIO.HIGH)
        Previous_State = 1
      variable.mutex.release()
      if Current_State==0 and Previous_State==1:
        # PIR has returned to ready state
        stop_time=time.time()  # update stop time
        #print " PIR went low "
        if time.time()-start_time > relay_off_delay:
          elapsed_time=int(stop_time-start_time)
          print "  Motion stopped " #print " " + (Elapsed time : " + str(elapsed_time) + " secs)"
          #GPIO.output(GPIO_relay1,GPIO.LOW)
          #GPIO.output(GPIO_relay2,GPIO.LOW) 
        Previous_State = 0

    fp.close()
    s.close()  
  except KeyboardInterrupt:
    print "  Quit"
    # Reset GPIO settings
    GPIO.cleanup()

