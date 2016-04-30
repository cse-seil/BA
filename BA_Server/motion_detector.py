# import the necessary packages
import argparse,sys
import datetime
import imutils
import time
import MySQLdb as mdb
import cv2
import socket
from timeit import Timer
from csv import writer
import sys
import multiprocessing 
import csv

'''
#print str(sys.argv[1])
#string_address ="rtsp://10.129."+str(sys.argv[1])+":1024/ISAPI/streaming/channels/101?auth=YWRtaW46MTIzNDU="
#print string_address
#cam = 'rtsp://10.129.23.97:1024/ISAPI/streaming/channels/101?auth=YWRtaW46MTIzNDU=' # LAB
cam = 'http://admin:seil12345@10.129.28.63:80/mjpeg.cgi?user=admin&password=seil12345&channel=0&.mjpg' # Dlink
#cam = 'rtsp://10.129.28.219:1024/ISAPI/streaming/channels/101?auth=YWRtaW46MTIzNDU=' # Lab wala in 304
cam="rtsp://10.129.23.97:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="#97(corner) # Lab
cam="rtsp://10.129.28.219:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU=" # lab wala in 304
cam = "rtsp://10.129.28.219:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU=" # lab wala in 304
2977
#cam="rtsp://10.129.11.225:554/ISAPI/streaming/channels/102?auth=YWRtaW46NTQzMjE=" #ERTS in 304
#cam = "rtsp://10.129.23.175:554/ISAPI/streaming/channels/101?auth=YWRtaW46YWRtaW4xMjM=" 
#cam = "http://10.129.28.45:80/videostream.asf?user=admin&pwd=seil12345&resolution=64&rate=0"  # Foscam
#cam = "http://10.129.28.45:80/videostream.asf?user=admin&pwd=seil12345&resolution=64&rate=0"
#cam = "rtsp://10.129.11.231:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU=" 
#cam = "rtsp://10.129.11.231:1024/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
#cam = "rtsp://10.129.23.176:1024/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
cam = "rtsp://10.129.23.176:554/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
#cam = "rtsp://10.129.23.174:1024/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
#cam = "rtsp://10.129.23.173:554/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
#cam = "rtsp://10.129.23.172:554/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
#cam = "rtsp://10.129.23.171:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
#camera = cv2.VideoCapture(cam)
'''

  
#if __name__ == '__main__' :
class WorkerProcess(multiprocessing.Process):
  def __init__(self, data_id,cam_url1,cam_url2,port,pr1_ip,pr1_port,pr2_ip,pr2_port):
    super(WorkerProcess, self).__init__()
    self.data_id = data_id
    self.cam_url1 = cam_url1
    self.cam_url2 = cam_url2


    con = mdb.connect("10.129.23.100" , "rohit" , "" , "BuildingAutomation")
    cur = con.cursor()
    cur.execute("select proxy_ip , proxy_listen_port  from proxy_info ;")
    row = cur.fetchone()
    self.ip_p1 = str(row[0])
    self.port_send_cfg = int(row[1])
    row = cur.fetchone()
    self.ip_p2 = str(row[0])
    self.port_send_p2 = int(row[1])
    print self.ip_p2 , self.port_send_p2
    con.close()
    self.ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    #self.ip_own = "10.129.23.161"#socket.gethostbyname(socket.gethostname())#"10.129.23.161"
    
    #self.ip_p1 = pr1_ip
    self.port_recv_p1 = int(port)
    #self.ip_p2 = pr2_ip
    #self.port_send_p2 = int(pr2_port)
    #self.port_send_cfg = int(pr1_port)
    self.HD = False
    with open("config_param_svr.cfg","r") as inf:
      t = inf.readline()
      field = inf.readline().split(" ")
      self.T_Restart = int(field[0])
      self.T_Check = int(field[1].replace("\n",""))
    self.T_standby = 2
    #HD = False
    self.startmain = time.time()
    self.sock_recv = ""#socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    self.sock_send = ""#socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #host = ''
    self.temp = ""

  def run(self):
    config_msg = "$add," + self.data_id + "P" + "," +  self.ip_own + "," + str(self.port_recv_p1) + ";"
    #sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #self.sock_send.sendto(config_msg, (self.ip_p1, self.port_send_cfg))
    #print "qqqqqqqqqqqq"
    #print self.port_recv_p1
    print self.ip_own,self.port_recv_p1
    self.sock_recv.bind((self.ip_own , self.port_recv_p1))
  
    #global HD
  
    
    #print "all done"
    while True:
        
      if not self.HD:
        data = self.sock_recv.recv(1024) # buffer size is 1024 bytes
        print data
        if "304" in data: #to remove for 304
          self.ip_p2 = "10.129.23.150"
          self.port_send_p2 = 6010
        if data[0] == "#" and data[-1] == ";":
          print data
          temp = data[1:-1].split(",")
          print temp
  
      if temp[1] == "T":
        data = 'reset'
        time.sleep(self.T_standby)
        self.HD1 = False
        self.HD2 = False
        self.HD = self.HD1 or self.HD2
        self.Camera_Occupancy(self.cam_url1,1)
        print "url2" + str(self.cam_url2) + "end"
        if self.cam_url2 != "":
          self.Camera_Occupancy(self.cam_url2,2)
        self.HD = self.HD1 or self.HD2
        #self.HD = True
        reply_msg = "#" + self.data_id + "I" + ","
        if(not self.HD):
          print self.HD
          reply_msg += "HND;"
          print self.ip_p2 , self.port_send_p2
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
        else:
          print self.HD
          reply_msg += "HD;"
          print self.ip_p2 , self.port_send_p2
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
          
        self.startmain = time.time()
  
  
  
      if (self.HD and (time.time() - self.startmain)>self.T_Restart):
        self.HD = False
        self.Camera_Occupancy(cam_url1,1)
        if self.cam_url2 != "":
          self.Camera_Occupancy(cam_url2,2)        
        
        self.HD = self.HD1 or self.HD2
        #self.HD = True
        reply_msg = "#" + self.data_id + "I" + ","
        if(not self.HD):
          print self.HD
          reply_msg += "HND;"
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
        else:
          print self.HD
          reply_msg += "HD;"
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
        self.startmain = time.time()
  
      k = cv2.waitKey(30) & 0xff
      if k == 27:
        break
        
  def Camera_Occupancy(self,cam_url,turn):
    HD_Timer =0
    #T_Check = 20
    if turn == 1:
      self.HD1 = False
    if turn == 2:
      self.HD2 = False
    ThresholdArea = 150
    frame_deletion = 150
    number_of_countours = 0
    connection = False
    # construct the argument parser and parse the arguments
    '''ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    args = vars(ap.parse_args())
    '''
    # if the video argument is None, then we are reading from webcam
    #if   args.get("video", None) is None:
    #camera = cv2.VideoCapture(0)
    
    #fgbg = cv2.BackgroundSubtractorMOG()
    #camera = cv2.VideoCapture('track.mp4')
    #time.sleep(1)

    # otherwise, we are reading from a video file
    #else:
      #camera = cv2.VideoCapture(args["video"])
    camera = cv2.VideoCapture(cam_url)
    #print "aaasdasdasda"
    start = time.time()
    # initialize the first frame in the video stream
    firstFrame = None

    while(not connection):
      try:
        ret, frame = camera.read()
        height,width,ch = frame.shape
        connection = True
      except:
        camera = cv2.VideoCapture(cam_url)
        print camera



    # loop over the frames of the video
    while True:
      # grab the current frame and initialize the occupied/unoccupied
      # text
      (grabbed, frame) = camera.read()
      if grabbed is None:
        print "waiting"
        continue
      else:
        startcheck = time.time()
      #frame = frame[85:610,:]
      #if(frame_deletion != 0):
        #frame_deletion = frame_deletion - 1
        #continue
        
      original_feed = frame 
      # if the frame could not be grabbed, then we have reached the end
      # of the video
      #if not grabbed:
        #break

      # resize the frame, convert it to grayscale, and blur it
      frame = imutils.resize(frame, width=500)
      #fgmask = fgbg.apply(frame)
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      gray = cv2.GaussianBlur(gray, (21, 21), 0)

      # if the first frame is None, initialize it
      if firstFrame is None:
        firstFrame = gray
        continue

      # compute the absolute difference between the current frame and
      # first frame
      frameDelta = cv2.absdiff(firstFrame, gray)
      firstframe = gray
      #thresh = cv2.threshold(frameDelta, 120, 255, cv2.THRESH_BINARY_INV)[1]
      thresh = cv2.adaptiveThreshold(frameDelta,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
                  #thresh = cv2.threshold(fgmask, 70, 255, cv2.THRESH_BINARY)[1]

      # dilate the thresh:olded image to fill in holes, then find contours
      # on thresholded image
      thresh = cv2.dilate(thresh, None, iterations=3)
      
      cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
      #cnts, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
      
      contourcheck = len(cnts)  
      # loop over the contours
      for i in range(len(cnts)):

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text. Ignore the areas smaller than A
        if(cv2.contourArea(cnts[i]) < ThresholdArea):
          contourcheck = contourcheck - 1
          continue
        (x, y, w, h) = cv2.boundingRect(cnts[i])
        
        cv2.drawContours(frame, cnts, i,(244,233,0))
        cv2.rectangle(frame, (x, y), (x + w, y + w), (0, 0, 255), 2)
        
      if (contourcheck>0):
        HD_Timer += 1
      else:
        HD_Timer = 0
              
      if HD_Timer >25:
        if turn == 1:
          self.HD1 = True
        if turn == 2:
          self.HD2 = True
        #print "HD = TRUE"
        # draw the text and timestamp on the frame
      # show the frame and record if the user presses a key    
      #if z<50:
      #  z += 1
      #  continue
      #print (time.time() - startcheck)
      cv2.imshow("Security Feed", frame)
      #cv2.imshow("BG Subtract", fgmask)
      #cv2.imshow("Thresh", thresh)
      #cv2.imshow("Frame Delta", frameDelta)
      #cv2.imshow("Original Feed",original_feed)
      key = cv2.waitKey(1) & 0xFF
      

      # if the `q` key is pressed, break from the lop
      #if HD or key == ord("q") or ((time.time() - start) >T_Check):
      
      if key == ord("q") or ((time.time() - start) >self.T_Check):
        '''
        reply_msg = "#" + self.data_id + "_I01" + ","
        if(not self.HD):
          print self.HD
          reply_msg += "HND;"
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
        else:
          print self.HD
          reply_msg += "HD;"
          self.sock_send.sendto(reply_msg , (self.ip_p2, self.port_send_p2))
          print reply_msg
        '''
        break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()

  '''
  def print_centroid(contour):
    M = cv2.moments(contour)
    if int(M['m00']) == 0:
      f1.writerow([-1,-1])
      return -1,-1
    cx = int(M['m10']/M['m00']) 
    cy = int(M['m01']/M['m00'])
    
    f1.writerow([cx,cy])  
    return cx, cy


  def FindLargestContour(contours):
    area_contours = [cv2.contourArea(contours[i]) for i in range(len(contours))]
    t = []
    for i in range(len(area_contours)):
      if area_contours[i] > 100:
        t.append(area_contours[i])
    
    return area_contours.index(max(t))
  '''  
    
def main(args):
  #print(args)
  pool = []
  dic = {4010:"C201R" ,4011:"C205R" ,4012:"C301R" ,4013:"C305R" , 4014:"C304R" }
  i = int(sys.argv[1]) #port of server processes , gets incremented by 1 for every new server process
  con = mdb.connect("10.129.23.100" , "rohit" , '' , "BuildingAutomation")
  cur = con.cursor()
  cur.execute("select proxy_ip , proxy_listen_port  from proxy_info ;")
  row = cur.fetchone()
  pr1_ip = str(row[0])
  pr1_port = int(row[1])
  row = cur.fetchone()
  pr2_ip = str(row[0])
  pr2_port = int(row[1])
  con.close()
  
  #inf = open("proxy_info.cfg","r")
  #tt1 = inf.readline().replace('\n','')
  #tt2 = tt1.split(' ')
  #pr1_ip = tt2[0]
  #pr1_port = int(tt2[1])
  #tt1 = inf.readline().replace('\n','')
  #tt2 = tt1.split(' ')
  #pr2_ip = tt2[0]
  #pr2_port = int(tt2[1])
  #print "wwwwwwwwwww"
  #print pr1_ip,pr1_port,pr2_ip,pr2_port
  

  with open("server.cfg","r") as inf:
    row = csv.reader(inf, delimiter=" ")
    for trow in row:
      data_id = trow[0]
      if dic[i] != data_id:
        continue
      cam_url1 = trow[1]
      cam_url2 = ""
      port = trow[2]
      if len(trow) == 4:
        cam_url2 = trow[2]
        port = trow[3]
      pool.append(WorkerProcess(data_id,cam_url1,cam_url2,i,pr1_ip,pr1_port,pr2_ip,pr2_port))
      break
    #  i += 1
      #data_id_list = [d_id for d_id in trow]
    
    #print data_id_list[0]
    
  
  # Create the "process pool"
  #pool = [WorkerProcess(i, 3) for i in data_id_list]#range(int(args[0]))]

  # Start all process
  for process in pool:
    process.start()
  
  # wait for process to die
  for process in pool:
    process.join()
  
    
if __name__ == '__main__':
  main(sys.argv[1:])  


