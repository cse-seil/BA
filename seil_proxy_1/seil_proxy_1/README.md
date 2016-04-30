# Data logger proxy.

## Primary function 

- Receive data from all sensing devices installed.
- Store the received data in plain text / CSV format.
- Change the logging parameters of the proxy without shutdown. 
- Forward the message "as it is" to the system that requested the data.

## Working
This proxy will listen for UDP messages on a port. It will not send any reply to the message sending device. This system will not send any command also to these devices.

Data will be an ASCII string. It will start with '#' and end with';'. Data between start and end character and should be separated by ','. First field of the data should be unique Data 'ID'. If the start and end marker are not found in the data at the correct location, message will logged to error file. 

#### Message Format

 - \#<Data ID>,<coma separated data>;

Log files will be named as <ID>_<dd-mm-yy>.csv, each day a new file will be created for each data ID. No configuration change will be required for adding new data ID. While logging the data to the CSV file, the start and end marker will be removed and a new column containing Unix epoch in milliseconds will be added initially after the ID.

Should IP address of the sender also be logged? 

#### CSV Data Format

 - <ID>,<epoch in milliseconds>,<coma separated data>

Configuration command can be sent to the proxy to its UDP port similar to data. Change in parameter "Listened port"  will need the proxy to be restarted.  Other parameters will take effect immediately without restarting the proxy. Syntax for command are 

 - $set,<parameter>,<value>;

This command will change the value of the parameter.

 - $add,<Device ID>,<Forwarding IP>,<Forwarding port>;

This command will add new forwarding address for the messages, Device ID could also be added as "*" to forward all messages. In case a device ID and * both are added for same IP, port combination only one message will be forwarded.

 - $delete,<Device ID>,<Forwarding IP>,<Forwarding port>;

This command will delete a forwarding address.

 - $shutdown;
 
Shutdown the server

## Files

- Seil_proxy.py

    UDP Server 

- c.py

    Sample client code in python, It can also be used to send test / command messages to the server.

-  main.c

    Sample client code in C

- config.py

usage: config.py [-h] [-s SET | -a ADD | -d DELETE]

optional arguments:

 - -h, --help  show help message and exit
 - -s SET      Where SET is <parameter>=<value>
 - -a ADD      Where ADD is <id>,<ip>,<port>
 - -d DELETE   Where DELETE is <id>,<ip>,<port>    

    Use this command without aguments to view the system parameters. Following parameters are available with -s option

     - Log file path                            path:  "/" separated folder path 
     
        if folder is not present it will be created
        
     - Listener Port                             port:  45678 (default)
     
Configurations changed using config.py will need server restart to take effect.
    
    
## Future work

- Test performance of the proxy and migration to cpp of required.

- Log file to be created in separate folder for each day or each data ID