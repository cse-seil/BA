import sqlite3 as db
import argparse

def getParams(db_string):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "SELECT id, name, value from db_params"
    
    #print("query is: ", query )
    cur.execute(query)
    rows = cur.fetchall()
    params = {}
    if  len(rows) > 0:
        for row in rows:
            params[row[0].rstrip()] = [row[1].rstrip(),row[2].rstrip()]
    conn.close()
    return params 


def setParam(db_string,id,val):
    conn = db.connect(db_string)
    cur = conn.cursor()
    query  = "UPDATE db_params set value  =? where id = ?"
    
    #print("query is: ", query )
    cur.execute(query,(val,id))
    conn.commit()
    conn.close()

    
def main(db_name):
#    db_name = "proxy.sqlite"
    #print(args)
    parser = argparse.ArgumentParser(description='UDP Proxy Config')
    group1 = parser.add_mutually_exclusive_group(required=False)
    group1.add_argument('-s', action="store", dest="set", help="Where SET is <parameter>=<value>")

    arguments = parser.parse_args()

    if arguments.set is not None:
        param_val = arguments.set.split("=")
        if len(param_val) != 2:
            print "expecting <parameter>=<value> got " ,arguments.set
            return
        else:
            setParam(db_name,param_val[0],param_val[1])
            print "Updated"


    g_params = getParams(db_name)
    print "----------------- Parameters -------------------------"
    for key in g_params:
        print  '%-20s%28s%-28s' % (g_params[key][0], key + ": ",g_params[key][1]) 
    print ""

    
if __name__ == '__main__':
    import sys
    print sys.argv[0],sys.argv[0].find("config_")
    if(sys.argv[0].find("config_") == 0):
        db_str = sys.argv[0].split(".")[0][7:] + ".sqlite"
    else:
        db_str = sys.argv[0].split(".")[0]  + ".sqlite"
    
    print db_str
    main(db_str)
    