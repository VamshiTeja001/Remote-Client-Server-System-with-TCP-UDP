# Remote-Client-Server-System-with-TCP-UDP
Contains files related to client server system implementation along with cache with data transmission over both TCP and UDP protocols. Python code has been used and Wireshark tool has been used to test and validate the system.


Brief Overview of Code working is given in client, cache and server codes as comments. 

Code Execution Steps:

For Server:
python3 server.py <server_port> <protocol>

For Cache:
python3 cache.py <cache_port> <server_host> <server_port> <protocol>

For Client: 
pyhton3 client.py <server_host>  <server_port> <cache_port> <cache_host> <protocol> 
