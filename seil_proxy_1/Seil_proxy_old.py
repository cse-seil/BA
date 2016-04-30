import socket
import MySQLdb as mdb
import sys
import time
import config
import os
import multiprocessing
from Queue import Queue 

db_name = "proxy.sqlite"
proxy_id = sys.argv[1]

class message:
    def __init__(self, ip, ts, millis, data):
        self.ip = ip
        self.ts = ts
        self.millis = millis
        self.data = data

def writeLog(folder,file,date,data):
    if not os.path.exists(folder):
        os.makedirs(folder)

    g = open(folder + file + "_" + date + ".csv","a")

    g.write(bytes(data + "\n"))
    g.close()
        
        
class logWriter(multiprocessing.Process):
    """ A logWriter that takes message  from a queue, 
        identifies if it is a command or data message.
        
        It will process command for changing the folder location of the log files.
        
        Any message (command or data) send to it will be logged to a seperate file for the message id.
            
        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, writer_q):
        super(logWriter, self).__init__()
        self.writer_q = writer_q

    def run(self):
        # As long as we weren't asked to stop, try to take new data from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        params = config.getParams(db_name)
        folder = params["path"][1]
        if folder[-1] != "/":
            folder = folder + "/"

        print "Writer Started"
        while True:
            print "Reading"
            msg = self.writer_q.get()
            if msg is None: # This will probably never reached 
                print "None Received"
                continue
#                self.writeLog(msg)
            # if it is message add timestamp to the message 
            if msg.data[0] == '#' and msg.data[-1] == ';': 
                col =  msg.data[1:-1].split(',')
                d_out  = col[0] + "," + str(msg.millis)  + "," + msg.ip + "," + ",".join(col[1:])
                file = col[0]
                writeLog(folder,file,msg.ts,d_out)
            elif msg.data[0] == '$' and msg.data[-1] == ';':
                print "$ message is QQQQQQQQQ" + msg.data
		# $ needs to be handled in a different way
                col =  msg.data[1:-1].split(',')
                file = col[0]
                d_out  = col[0] + "," + str(msg.millis)  + "," + msg.ip + "," + ",".join(col[1:])
                writeLog(folder,file,msg.ts,d_out)
                if col[0] == "shutdown":
                    break;
                if col[0] == "set":
                    if len(col) == 3:
                        config.setParam(db_name,col[1],col[2])
                        params = config.getParams(db_name)
                        folder = params["path"][1]
                        if folder[-1] != "/":
                            folder = folder + "/"
                        
            else:
                file = "Error"
                d_out  = str(msg.millis)  + "," + msg.ip + "," + msg.data
                writeLog(folder,file,msg.ts,d_out)


            print "logWriter", msg.data
#            if msg.data == "%":
#                break;
     

class forwarder(multiprocessing.Process):
    """ A logWriter that takes message  from a queue, 
        identifies if it is a command or data message.
        
        It will process command for changing the folder location of the log files.
        
        Any message (command or data) send to it will be logged to a seperate file for the message id.
            
        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, fwd_q):
        super(forwarder, self).__init__()
        self.fwd_q = fwd_q

    def run(self):
        # As long as we weren't asked to stop, try to take new data from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.

        print "forwarder Started"
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print 'Failed to create socket'
            return

        
        loead_clients = True
        while True:
            if loead_clients:
                clients = config.getClients(db_name)
                c_id = {}
                for r in clients:
                    if r[0] in c_id:
                        c_id[r[0]].append([r[1],r[2]])
                    else:
                        c_id[r[0]] = [[r[1],r[2]]]        
                loead_clients = False
                
            print "Reading"
            message = self.fwd_q.get()
            if message is None: # This will probably never reached 
                print "None Received"
                continue
#                self.writeLog(message)
            print "forwarder", message.data
            if message.data == "%":
                break;

            if message.data[0] == '#' and message.data[-1] == ';': 
                col =  message.data[1:-1].split(',')
                target_clients = []
                if col[0] in c_id:
                    target_clients = target_clients + c_id[col[0]] 
                if "*" in c_id:
                    target_clients = target_clients + c_id["*"] 
                    
                for client in target_clients:
                    try :
                        client_socket.settimeout(2)
                        print "M2 sent is: " + message.data
                        client_socket.sendto(message.data, (client[0], client[1]))
                        print "Sending to" ,client[0], client[1]
                    except socket.error, msg:
                        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                    except socket.timeout:
                        print("Timeout")

            elif message.data[0] == '$' and message.data[-1] == ';':
                col =  message.data[1:-1].split(',')
                if col[0] == "shutdown":
                    break;
                if col[0] == "add":
                    if len(col) == 4:
                        config.addClient(db_name,col[1],col[2],col[3])
                        loead_clients = True
                if col[0] == "delete":
                    if len(col) == 4:
                        config.delClient(db_name,col[1],col[2],col[3])
                        loead_clients = True

                        
                
class UDPListner(multiprocessing.Process):
    """ A UDPListner that receives UDP message on a port, 
        It records the time when the message is received and put the mesage to two queues for 
            1. Log writing
            2. Message forwarding
           
        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, writer_q, fwd_q):
        super(UDPListner, self).__init__()
        self.writer_q = writer_q
        self.fwd_q = fwd_q

    def run(self):

        HOST = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

        g_params = config.getParams(db_name)

        # Listning port
        PORT = int(g_params["port"][1]) 

        #insert proxy ip , port in datbase

        try:
          con = mdb.connect('10.129.23.100', 'rohit' , '' , 'BuildingAutomation'  )
          
          cur = con.cursor()
          cur.execute("select count(*) from proxy_info where proxy_id = %s ;",("proxy_" + str(proxy_id)))
          row = cur.fetchone()

          if str(row[0]) == "0":
            cur.execute("insert into proxy_info values(%s,%s,%s);",('proxy_'+proxy_id,HOST,str(PORT)))
            con.commit()

        except mdb.Error, e:
          
          print "Error %d: %s" % (e.args[0], e.args[1])
          sys.exit(1)
        
        finally:
          if con:
            con.close()
        # Datagram (udp) socket
        try :
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            #sys.exit()
            return
         
        print 'Socket created'
         
        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error , msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            #sys.exit()
            return
             
        print 'Socket bind complete'

        # As long as we weren't asked to stop, try to take new data from the
        # UDP socket and put the message to the queues.
        while True:
            d = s.recvfrom(1024)
            print "message received is " + str(d)
            millis = int(round(time.time() * 1000))
            
            ts = time.strftime("%d-%m-%Y")
            msg = message(d[1][0],ts,millis,d[0])
            #print "Putting", d

            self.writer_q.put(msg)
            self.fwd_q.put(msg)
            
            if msg.data == "%" or msg.data == "$shutdown;":
                break;

     
def UDP_servver():
    
    #print "writing to ",s

    if server1_port > 0:
        try :
            c.settimeout(2)
            print "M1 snet is: " + data
            c.sendto(data, (server1_ip, server1_port))
        except socket.error, msg:
            print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        except socket.timeout:
            print("Timeout closing socket")
    #    reply = 'OK...' + data
     
    #s.sendto(reply , addr)
    print d
    #print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
         
    
def main(args):
    #print(args)
    
    #UDP_servver()
    writer_q = multiprocessing.Queue()
    fwd_q = multiprocessing.Queue()

    writer = logWriter(writer_q)
    listner = UDPListner(writer_q,fwd_q)
    fwd = forwarder(fwd_q)
    
    
    writer.start()
    fwd.start()
    listner.start()
    
    fwd.join()
    writer.join()
    listner.join()
    
    
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])   
