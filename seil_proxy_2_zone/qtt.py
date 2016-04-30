import MySQLdb as mdb

proxy_id = 02
try:
  con = mdb.connect('10.129.23.100', 'rohit' , '' , 'BuildingAutomation'  )
  
  cur = con.cursor()
  qq = "proxy_02"# + str(proxy_id)
  tt = cur.execute("select count(*) from proxy_info where proxy_id = %s ;",(qq))#"proxy_" + proxy_id,))#select 	hport from proxy_info where proxy_	id = " + "")
  #result = tt.fetchone()#use_result()
  print "hihihihi"
  print tt#result

  cur.execute("insert into proxy_info values(%s,%s,%s);",('proxy_'+ str(proxy_id),HOST,str(PORT)))#SELECT proxy_ip , proxy_listen_port from proxy_info where proxy_	id = " + "")

except mdb.Error, e:
  
  print "Error %d: %s" % (e.args[0], e.args[1])
  sys.exit(1)

finally:
  if con:
    con.close()
