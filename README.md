# rospynode
A python class to connect to ROS (1 or 2) using rosbridge v2.0 Protocol
# Problem statement
There is an application in windows that needs to connect to ROS. 
# Intruduction
This work is inspired by [roslibpy](https://github.com/gramaziokohler/roslibpy). First I started using roslibpy for my application. The problem that I have with it was it had a feature to reconnect when connection from client to server was down. So, sometimes reconnect was happening with latency and I didn't know when to give up and reconnect.
I needed full control and flexibility to open or close the connection whenever needed. This project was created to address this need. It allows the user to start the connection, check the connection, reconnect if connection is down and disconnect.
This program is according to the [rosbridge V2.0 Protocol](https://github.com/RobotWebTools/rosbridge_suite/blob/develop/ROSBRIDGE_PROTOCOL.md) guidlines so it can be used to connect to ROS 1 and 2 both. The following APIs are implemented so far:  
1- advertise  
2- publish  
3- unadvertise  
4- subscribe  
5- unsubscribe  
# Basic usage  
```python
from rospynode import Client
myclient = Client(host='192.168.1.10', port=9090)  # Define IP address and port of the rosbridge server
myclient.connect()  # Request to connect
if myclient.is_connected == True:
  # do your tasks such as advertising, publishing
else:
  # Attempt to reconnect
```
  
