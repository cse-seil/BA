#!/usr/bin/python
import time
import RPi.GPIO as GPIO
import os
import glob
import variable
from PIR import *
from threading import Thread, Lock


def temp_param_init():
  with open("/home/pi/Final_code/config_param_rpi.cfg","r") as inf:
    t = inf.readline() # ignore first line
    field = inf.readline().split(" ")
    variable.ulimit = float(field[0])
    variable.llimit = float(field[1])
    variable.flimit = float(field[2])
    variable.set_point = float(field[3].replace("\n",""))


def temp_init():
  #initializing the temperature sensor to collect the readings
  sensorBase = "/sys/bus/w1/devices/28*"
  os.system('sudo modprobe w1-gpio')
  os.system('sudo modprobe w1-therm')
  sensors=glob.glob(sensorBase)
  time.sleep(3)
  count = 1
  arr = []
  sensorList = []
  for i in sensors:
      #global arr
      arr.append(i.split('/')[5])
      arr.append(str(count))
      sensorList.append(arr)
      arr = []
      count = count + 1
  return sensorList


#fetching temperature from the device file of the temperature sensor
def get_Temp(sensorList):
  deviceFile='/sys/bus/w1/devices/'+sensorList[0][0]+'/w1_slave'
  f = open(deviceFile, 'r')
  lines = f.readlines()
  f.close()
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = readTempRaw(deviceFile)
  equalsPos = lines[1].find('t=')
  if equalsPos != -1:
    tempString = lines[1][equalsPos+2:]
    tempC = float(tempString) / 1000.0
  variable.Temp = tempC
  return tempC


def relay_code():
	# Use BCM GPIO instead of physical pin numbers
  temp_param_init()
  sensorList = temp_init()
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  #global GPIO_relay1
  GPIO_fan1 = 17 # output pin for controlling fan relay
  GPIO_fan2 = 27
  GPIO_fan3 = 22
  GPIO_fan4 = 5
  GPIO_fan5 = 24
  GPIO_fan6 = 25
  
  GPIO_L1 = 6
  GPIO_L2 = 13
  GPIO_L3 = 19
  GPIO_L4 = 26
  GPIO_L5 = 23
  GPIO_relay1 = 20
  GPIO_AC1 = 16
  GPIO_AC2 = 20
  GPIO_AC3 = 21
  
  #set fan relay gpio pin as output, with initial state = 0 
  print variable.automate
  if(variable.automate):
    GPIO.setup(GPIO_fan1, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_fan2, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_fan3, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_fan4, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_fan5, GPIO.OUT, initial=0)
    GPIO.setup(GPIO_fan6, GPIO.OUT, initial=0)
  
    GPIO.setup(GPIO_L1, GPIO.OUT, initial = 0)
    GPIO.setup(GPIO_L2, GPIO.OUT, initial = 0)
    GPIO.setup(GPIO_L3, GPIO.OUT, initial = 0)
    GPIO.setup(GPIO_L4, GPIO.OUT, initial = 0)
    GPIO.setup(GPIO_L5, GPIO.OUT, initial = 0)
  
    GPIO.setup(GPIO_AC1, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_AC2, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_AC3, GPIO.OUT, initial = 1)
    variable.mutex.acquire()
    variable.Light_State = False
    variable.Fan_State = False
    variable.AC_State = False
    variable.mutex.release()


  if(not variable.automate):
    GPIO.setup(GPIO_fan1, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_fan2, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_fan3, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_fan4, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_fan5, GPIO.OUT, initial=1)
    GPIO.setup(GPIO_fan6, GPIO.OUT, initial=1)
  
    GPIO.setup(GPIO_L1, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_L2, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_L3, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_L4, GPIO.OUT, initial = 1)
    GPIO.setup(GPIO_L5, GPIO.OUT, initial = 1)
  
  
    #GPIO.setup(GPIO_AC1, GPIO.OUT, initial = 1)
    #GPIO.setup(GPIO_AC2, GPIO.OUT, initial = 1)
    #GPIO.setup(GPIO_AC3, GPIO.OUT, initial = 1)
  global Current_State
  time.sleep(3)
  try:
  
    print " I'm in relay code ! "
    while True:
      variable.mutex.acquire()  

      if variable.HD :
        GPIO.output(GPIO_L1,GPIO.HIGH)
        GPIO.output(GPIO_L2,GPIO.HIGH)
        GPIO.output(GPIO_L3,GPIO.HIGH)
        GPIO.output(GPIO_L4,GPIO.HIGH)
        GPIO.output(GPIO_L5,GPIO.HIGH)
        try:
          tempC = get_Temp(sensorList) # our code to retreive current temp
        except:
          print "inside EXCEPT !!!!!!!!!!"
          tempC = 41.0
        print "TEMPTEMPTEMPTEMP" , tempC
        if tempC < 10 or tempC >= 40:
          tempC = 41.7
        variable.Temp = tempC
        variable.Light_State = True
          #print "in" + str(variable.HD)
        print tempC
        # turn ON fan if current temperature is more than the set threshold value in
        if tempC >= variable.flimit:
          print "FAN ON"
          variable.Fan_State = True
          if(variable.automate):
            GPIO.output(GPIO_fan1,GPIO.HIGH)
            GPIO.output(GPIO_fan2,GPIO.HIGH)
            GPIO.output(GPIO_fan3,GPIO.HIGH)
            GPIO.output(GPIO_fan4,GPIO.HIGH)
            GPIO.output(GPIO_fan5,GPIO.HIGH)
            GPIO.output(GPIO_fan6,GPIO.HIGH)
        else:
          print "FAN OFF"
          variable.Fan_State = False
          if(variable.automate):
            GPIO.output(GPIO_fan1,GPIO.LOW)
            GPIO.output(GPIO_fan2,GPIO.LOW)
            GPIO.output(GPIO_fan3,GPIO.LOW)
            GPIO.output(GPIO_fan4,GPIO.LOW)
            GPIO.output(GPIO_fan5,GPIO.LOW)
            GPIO.output(GPIO_fan6,GPIO.LOW)
        if tempC >= variable.ulimit:
          print "Its "+str(tempC)+" : Turn ----> ON"
          if(variable.automate):
            GPIO.output(GPIO_AC1, GPIO.LOW)
            GPIO.output(GPIO_AC2, GPIO.LOW)
            GPIO.output(GPIO_AC3, GPIO.LOW)
          variable.AC_State = True
        elif tempC <= variable.llimit:
          print "Its "+str(tempC)+" : Turn ----> OFF"
          if(variable.automate):
            GPIO.output(GPIO_AC1,GPIO.HIGH)
            GPIO.output(GPIO_AC2,GPIO.HIGH)
            GPIO.output(GPIO_AC3,GPIO.HIGH)
          variable.AC_State = False
        else:
          print "Its "+str(tempC)+" : OK :)"
      if not variable.HD and not variable.Cam_Standby:
		    # do ALL appliance OFF
        if(variable.automate):
          GPIO.output(GPIO_fan1,GPIO.LOW)
          GPIO.output(GPIO_fan2,GPIO.LOW)
          GPIO.output(GPIO_fan3,GPIO.LOW)
          GPIO.output(GPIO_fan4,GPIO.LOW)
          GPIO.output(GPIO_fan5,GPIO.LOW)
          GPIO.output(GPIO_fan6,GPIO.LOW)
       
          GPIO.output(GPIO_L1,GPIO.LOW)
          GPIO.output(GPIO_L2,GPIO.LOW)
          GPIO.output(GPIO_L3,GPIO.LOW)
          GPIO.output(GPIO_L4,GPIO.LOW)
          GPIO.output(GPIO_L5,GPIO.LOW)
       
          GPIO.output(GPIO_AC1,GPIO.HIGH)
          GPIO.output(GPIO_AC2,GPIO.HIGH)
          GPIO.output(GPIO_AC3,GPIO.HIGH)

        variable.Light_State = False
        variable.Fan_State = False
        variable.AC_State = False
      variable.mutex.release()
  except KeyboardInterrupt:
    print " Interrupt --> exiting "
    # Reset GPIO settings
    GPIO.cleanup()
