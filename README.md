# rospynode
A python (version2 and 3) class to connect to ROS (1 or 2) using rosbridge v2.0 Protocol
# Problem statement
There is an application in windows that needs to connect to the ROS network. This class can help with that.
# Introduction
This work is inspired by [roslibpy](https://github.com/gramaziokohler/roslibpy). First I started using roslibpy for my application. The problem that I have with roslibpy was that it had a feature to reconnect automatically when connection from client to server was down. So, sometimes auto reconnect was happening with latency and I didn't know when to give up and reconnect by demand. Sometimes, if I wanted to disconnect, the auto reconnect was overruling my command.
I needed the full control and flexibility to open or close the connection whenever needed. This project was created to address that need. It allows the user to start the connection, check the connection, reconnect if connection is down, and disconnect the connection.
This program is according to the [rosbridge V2.0 Protocol](https://github.com/RobotWebTools/rosbridge_suite/blob/develop/ROSBRIDGE_PROTOCOL.md) guidelines so it can be used to connect to ROS 1 and 2 both. The following APIs are implemented so far:  
1- advertise  
2- publish  
3- unadvertise  
4- subscribe  
5- unsubscribe  
# Prerequisite
Install websocket-client module from [here](https://github.com/websocket-client/websocket-client).
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
  
