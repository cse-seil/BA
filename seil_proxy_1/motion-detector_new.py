# import the necessary packages
import argparse,sys
import datetime
import imutils
import time
import cv2
import socket
from timeit import Timer
from csv import writer
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE
sock = socket.socket(socket.AF_INET, # Internet
socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
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
cam = "rtsp://10.129.23.176:1024/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
cam = "rtsp://10.129.23.176:554/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
cam = "rtsp://10.129.23.174:1024/ISAPI/streaming/channels/102?auth=YWRtaW46YWRtaW4xMjM="
cam = "rtsp://10.129.23.173:554/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
cam = "rtsp://10.129.23.172:554/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
cam = "rtsp://10.129.23.171:1024/ISAPI/streaming/channels/102?auth=YWRtaW46MTIzNDU="
#camera = cv2.VideoCapture(cam)

print "here:"
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


def Camera_Occupancy():
	global HD
	HD_Timer =0
	T_Check = 20
	HD = False
	ThresholdArea = 150
	frame_deletion = 150
	number_of_countours = 0
	# construct the argument parser and parse the arguments
	'''ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", help="path to the video file")
	ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
	args = vars(ap.parse_args())
	'''
	# if the video argument is None, then we are reading from webcam
	#if 	args.get("video", None) is None:
	#camera = cv2.VideoCapture(0)
	
	#fgbg = cv2.BackgroundSubtractorMOG()
	#camera = cv2.VideoCapture('track.mp4')
	#time.sleep(1)

	# otherwise, we are reading from a video file
	#else:
		#camera = cv2.VideoCapture(args["video"])
	camera = cv2.VideoCapture(cam)
	print "aaasdasdasda"
	start = time.time()
	# initialize the first frame in the video stream
	firstFrame = None
	
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
			HD = True
			print "HD = TRUE"
			# draw the text and timestamp on the frame
		# show the frame and record if the user presses a key		
		#if z<50:
		#	z += 1
		#	continue
		print (time.time() - startcheck)
		cv2.imshow("Security Feed", frame)
		#cv2.imshow("BG Subtract", fgmask)
		cv2.imshow("Thresh", thresh)
		cv2.imshow("Frame Delta", frameDelta)
		cv2.imshow("Original Feed",original_feed)
		key = cv2.waitKey(1) & 0xFF
		

		# if the `q` key is pressed, break from the lop
		#if HD or key == ord("q") or ((time.time() - start) >T_Check):
		if key == ord("q") or ((time.time() - start) >T_Check):
			reply_msg = "#" + data_id + "_I01" + ","
			if(not HD):
				print HD
				reply_msg += "HND;"
				sock_send.sendto(reply_msg , (ip_p2, port_p2))
			else:
				print HD
				reply_msg += "HD;"
				sock_send.sendto(reply_msg , (ip_p2, port_p2))
			break

	# cleanup the camera and close any open windows
	camera.release()
	cv2.destroyAllWindows()
	
if __name__ == '__main__' :
	
	ip_own = "10.129.23.31"
	ip_p1 = "127.0.0.1"
	port_p1 = 5006
	ip_p2 = "127.0.0.1"
	port_p2 = 5007
	port_listen = 55555
	data_id = "SIC304_R1"
    
	config_msg = "$" + data_id + "," + str(ip_own) + "," + str(port_p1) + "," +  "_s01;"


    	sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    	sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    	sock_send.sendto(config_msg, (ip_p1, port_p1))
	sock_recv.bind((ip_own , port_listen))

	global HD
    
	T_Restart = 2
	T_standby = 2
	HD = False
	startmain = time.time()
	host = ''
	
	#port = int(sys.argv[1])#5005	
	#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	#s.bind((host,port))

	#s.listen(10)

	#conn, addr = s.accept()
	print "all done"
	while True:
			
		if not HD:
			data = sock_recv.recv(1024) # buffer size is 1024 bytes
			
			if data[0] == "#" and data[-1] == ";":
				temp = data[1:-1].split(",")
		
		if temp[1] == "T":
			print data
			data = 'reset'
			time.sleep(T_standby)
			HD = False
			Camera_Occupancy()
			startmain = time.time()



		if (HD and (time.time() - startmain)>T_Restart):
			HD = False
			Camera_Occupancy()
			startmain = time.time()

		k = cv2.waitKey(30) & 0xff
		if k == 27:
			break
	
	
