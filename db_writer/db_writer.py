import socket
import sys
import time
import config_db_writer as config
import os
import multiprocessing
from Queue import Queue 
import MySQLdb as mdb


class message:
    def __init__(self, ip, ts, millis, data):
        self.ip = ip
        self.ts = ts
        self.millis = millis
        self.data = data

        
class logWriter(multiprocessing.Process):
    """ A logWriter that takes message  from a queue, 
        identifies if it is a command or data message.
        
        It will process command for changing the folder location of the log files.
        
        Any message (command or data) send to it will be logged to a seperate file for the message id.
            
        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, writer_q,db_name):
        super(logWriter, self).__init__()
        self.writer_q = writer_q
        self.db_name = db_name
        self.params = config.getParams(self.db_name)
        

    def run(self):
        # As long as we weren't asked to stop, try to take new data from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        folder = self.params["path"][1]
        if folder[-1] != "/":
            folder = folder + "/"

        print "DB Writer Started"
        while True:
            print "Reading"
            msg = self.writer_q.get()
            if msg is None: # This will probably never reached 
                print "None Received"
                continue
            else:
                print "Received", msg
#                self.writeLog(msg)
            # if it is message add timestamp to the message 
            if msg.data[0] == '#' and msg.data[-1] == ';': 
                col =  msg.data[1:-1].split(',')
                d_out  = col[0] + "," + str(msg.millis)  + "," + msg.ip + "," + ",".join(col[1:])
                file = col[0]
                self.writeLog(folder,file,msg.ts,d_out)
                if len(col) <= 20:
                    self.writeDB(msg)
            elif msg.data[0] == '$' and msg.data[-1] == ';':
                col =  msg.data[1:-1].split(',')
                file = col[0]
                d_out  = col[0] + "," + str(msg.millis)  + "," + msg.ip + "," + ",".join(col[1:])
                self.writeLog(folder,file,msg.ts,d_out)
                if col[0] == "shutdown":
                    break;
            else:
                file = "Error"
                d_out  = str(msg.millis)  + "," + msg.ip + "," + msg.data
                self.writeLog(folder,file,msg.ts,d_out)


            print "logWriter", msg.data
#            if msg.data == "%":
#                break;
                        
    def writeLog(self,folder,file,date,data):
        if not os.path.exists(folder):
            os.makedirs(folder)

        g = open(folder + file + "_" + date + ".csv","a")

        g.write(bytes(data + "\n"))
        g.close()

    def writeDB(self, msg):
        print msg.ip, msg.ts,msg.millis
        fields =  msg.data[1:-1].split(",")
        fields = [fields[0]] + [str(msg.millis)] + fields[1:]
        print fields
        try:
            print "connecting to", self.params["mdb_server"][1], self.params["mdb_user"][1] , self.params["mdb_password"][1] , self.params["mdb_schema"][1]
            con = mdb.connect(self.params["mdb_server"][1], self.params["mdb_user"][1] , self.params["mdb_password"][1] , self.params["mdb_schema"][1]  )
            cur = con.cursor()
            cur.execute("select count(*) from data_log where class_id = %s ;",(fields[0],))
            row = cur.fetchone()
            if str(row[0]) == "0":
                data_values = (fields + ["" for x in range(22-len(fields))])
                query ="insert into data_log values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                print "Fields", query, data_values
                cur.execute(query,data_values)
                con.commit()
            else:
                data_values = (fields[1:] + ["" for x in range(22-len(fields))] + [fields[0]])
                query = "update data_log set ts = %s, " + ",".join(["d" + str(x) +"=%s" for x in range(1,21)]) + " where class_id = %s;"
                print query
                cur.execute(query,data_values)
                con.commit()

        except mdb.Error, e:
      
            print "Error %d: %s" % (e.args[0], e.args[1])
            return
    
#        finally:
#            if con:
#                con.close()

        con.close()
    
class UDPListner(multiprocessing.Process):
    """ A UDPListner that receives UDP message on a port, 
        It records the time when the message is received and put the mesage to two queues for 
            1. Log writing
            2. Message forwarding
           
        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, writer_q, db_name):
        super(UDPListner, self).__init__()
        self.writer_q = writer_q
        self.db_name = db_name

    def run(self):

#        HOST = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

        g_params = config.getParams(self.db_name)
        
        # Listning port
        PORT = int(g_params["port"][1]) 
        HOST = g_params["ip"][1]

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
            millis = int(round(time.time() * 1000))
            
            ts = time.strftime("%d-%m-%Y")
            msg = message(d[1][0],ts,millis,d[0])
            print "Putting", d

            self.writer_q.put(msg)
            
            if msg.data == "%" or msg.data == "$shutdown;":
                break;

     
def UDP_servver():
    
    #print "writing to ",s

    if server1_port > 0:
        try :
            c.settimeout(2)
            c.sendto(data, (server1_ip, server1_port))
        except socket.error, msg:
            print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        except socket.timeout:
            print("Timeout closing socket")
    #    reply = 'OK...' + data
     
    #s.sendto(reply , addr)
    print d
    #print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
         
    
def main(db_str):
    
    #UDP_servver()
    writer_q = multiprocessing.Queue()

    writer = logWriter(writer_q,db_str)
    listner = UDPListner(writer_q,db_str)
    
    
    writer.start()
    listner.start()
    
    writer.join()
    listner.join()
    
    
if __name__ == '__main__':
    import sys
    print sys.argv[0],sys.argv[0].find("config_")
    if(sys.argv[0].find("config_") == 0):
        db_str = sys.argv[0].split(".")[0][7:] + ".sqlite"
    else:
        db_str = sys.argv[0].split(".")[0]  + ".sqlite"
    
    print db_str

    main(db_str)   
