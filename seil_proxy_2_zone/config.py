import sqlite3 as db
import argparse

def getParams(db_string):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "SELECT id, name, value from proxy_params"
    
    #print("query is: ", query )
    cur.execute(query)
    rows = cur.fetchall()
    params = {}
    if  len(rows) > 0:
        for row in rows:
            params[row[0].rstrip()] = [row[1].rstrip(),row[2].rstrip()]
    conn.close()
    return params 


def getClients(db_string):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "select * from fwd_address where id == '*' union select * from fwd_address where id != '*' and ip|port not in (select ip|port from fwd_address where id  = '*')"
    
    #print("query is: ", query )
    cur.execute(query)
    rows = cur.fetchall()
    params = []
    if  len(rows) > 0:
        for row in rows:
            params.append([row[0].rstrip(),row[1].rstrip(),row[2]])
    conn.close()
    return params 

    
def setParam(db_string,id,val):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "UPDATE proxy_params set value  =? where id = ?"
    
    #print("query is: ", query )
    cur.execute(query,(val,id))
    conn.commit()
    conn.close()


def addClient(db_string,id,ip,port):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "insert into fwd_address values(?,?,?)"
    
    print("query is: ", query ,id,ip,port)
    cur.execute(query,(id,ip,port))
    conn.commit()
    conn.close()

    
def delClient(db_string,id,ip,port):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "delete from fwd_address where id  = ? and ip = ? and port = ?"
    
    #print("query is: ", query ,id,ip,port)
    cur.execute(query,(id,ip,port))
    conn.commit()
    conn.close()

    
def main(args):
    db_name = "proxy.sqlite"
    #print(args)
    parser = argparse.ArgumentParser(description='UDP Proxy Config')
    group1 = parser.add_mutually_exclusive_group(required=False)
    group1.add_argument('-s', action="store", dest="set", help="Where SET is <parameter>=<value>")
    group1.add_argument('-a', action="store", dest="add", help="Where add is <id>,<ip>,<port>")
    group1.add_argument('-d', action="store", dest="delete", help="Where add is <id>,<ip>,<port>")

    arguments = parser.parse_args()

    if arguments.set is not None:
        param_val = arguments.set.split("=")
        if len(param_val) != 2:
            print "expecting <parameter>=<value> got " ,arguments.set
            return
        else:
            setParam(db_name,param_val[0],param_val[1])
            print "Updated"

    if arguments.add is not None:
        param_val = arguments.add.split(",")
        if len(param_val) != 3:
            print "expecting <id>,<ip>,<port> got ",arguments.add 
            return
        else:
            addClient(db_name,param_val[0],param_val[1],param_val[2])
            print "Added"
            
            
    if arguments.delete is not None:
        param_val = arguments.delete.split(",")
        if len(param_val) != 3:
            print "expecting <id>,<ip>,<port> got ", arguments.delete
            return
        else:
            delClient(db_name,param_val[0],param_val[1],param_val[2])
            print "Deleted"


    g_params = getParams(db_name)
    print "----------------- Parameters -------------------------"
    for key in g_params:
        print  '%-20s%28s%-28s' % (g_params[key][0], key + ": ",g_params[key][1]) 
    print ""
    print "-------------- Servers Connected ---------------------"
    
    g_clients = getClients(db_name)
    c_id = {}
    
    for r in g_clients:
        if r[0] in c_id:
            c_id[r[0]].append([r[1],r[2]])
        else:
            c_id[r[0]] = [[r[1],r[2]]]
    
    print c_id
    for data in g_clients :
        print  '%-20s%29s%-28s' % (data[0], data[1]+":" ,data[2]) 
        
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
    