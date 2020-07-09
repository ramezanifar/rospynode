import websocket
import json
import time
import threading
import logging

class Client:
    '''This class creates a ROS client that connects to ROS network via rosbridge'''
    def __init__(self,traceable=True, handler=logging.NullHandler(), host='localhost', port=9090):
        # Initializations
        self.url = "ws://{}:{}".format(host, port)  # web socket url
        self.request_to_connect = False  # This flag is used as a command and initiates a connection to server
        self.is_connected = False  # This flag shows whether this client is connected to the rosbridge server
        self.is_connecting = False  # This flag is used to show when client is trying to connect to rosbridge. So it is busy. It is a transiton from not connected to connected. When this flag is true, a new command to connect to the server should not be issued
        self.is_running = True  # This flag determines to run or terminate the program (to safely exit the thread)
        self.subs = []  # Holds the info of all subscriber
        self.pubs = []  # Holds the info of all publishers
        # Logger settings
        self.logger = logging.getLogger('client')  # reference to the same handler
        self.logger.setLevel(logging.DEBUG)
        # Determine what logging handle to be used
        if traceable == False:  # If traceability is disabled logger is null.
            self.logger.addHandler(logging.NullHandler())
        elif traceable == True and type(handler) == logging.NullHandler:  # If enabled but not specified, we use a default setting.
            new_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            new_handler.setFormatter(formatter)
            self.logger.addHandler(new_handler)
            self.logger.info("ROS client started")
        else:  # Use the input logging handler
            self.logger.addHandler(handler)
        # Websocket settings
        websocket.enableTrace(traceable=traceable,handler=self.logger)  # Handle the logging
        ws_thread = threading.Thread(target=self.ws_run, args=(1,))  # This thread keeps the client running
        ws_thread.start()  # Start the thread


    def connect(self):
        # This method is used to connect client to server
        self.logger.info("Connect request received")
        self.ws = websocket.WebSocketApp("self.url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open)
        self.request_to_connect = True  # This flag is used to run the run_forever() method of the websocket class

    def on_open(self):
        # This method is invoked when client is connected to the server
        self.logger.info("Client connection to the server is open")
        self.is_connected = True
        self.is_connecting = False  # Reset the flag for next time use


    def on_message(self, message):
        # This method is invoked when a message comes from the server
        msg = json.loads(message)
        if msg["op"] == "publish":  # A message is published from server to the client
            for this_sub in self.subs:
                if this_sub['topic'] == msg['topic']:
                    this_sub['callback'](msg)


    def on_error(self, error):
        # This method is invoked when there is an error
        self.logger.error(error)

    def on_close(self):
        # This method is invoked when client connection closes
        self.logger.info("Client connection to the server is closed")
        self.is_connected = False
        self.is_connecting = False

    def ws_run(self,arg):
        # This is the thread that keeps the client connection running
        self.logger.info('Ready to start ws listener. Waiting for connect request ...')
        # Trap the thread in a loop
        while self.is_running == True:  # Keep this thread alive as long application is running
            if self.request_to_connect == True:  # Is there a request to connect or reconnect?
                self.logger.info('Attempting to (re)connect')
                self.is_connecting = True  # When this flag is True, requester should not issue another connect command
                self.request_to_connect = False  # Reset for next time use
                self.ws.run_forever()  # This is a blocking call
                self.logger.info("Web socket is closed. Try to reconnect")
            else:
                time.sleep(1)  # Give CPU a break before checking whether reconnect request has come


    def disconnect(self):
        #  This method is called when web program is supposed to finish
        self.logger.info("Disconnect request received")
        if self.is_connected == True:
            self.ws.close()  # close the websocket
            self.is_running = False

    def subscribe(self,topic,data_type,callback):
        # This method is used to subscribe to a topic
        # The following dictionary is according to ros bridge protocol
        found = False  # Initialization
        for this_sub in self.subs:  # Loop through all existing subscribed topics
            if this_sub['topic'] == topic:
                found = True
                break  # We found it. Terminate the loop
        if found == False:
            self.subs.append({'topic':topic,'callback':callback})

        # Message body according to the roswebsocket v2 protocol
        req={"op": "subscribe",
        "topic": topic,
        "type":data_type
        }
        msg_str=json.dumps(req)  # Dictionary to json
        self.ws.send(msg_str)  # Send to server

    def unsubscribe(self,topic):
        # This method is used to unsubscribe a topic
        for this_sub in self.subs:  # Loop through all existing subscribed topics
            if this_sub['topic'] == topic:
                self.subs.remove(this_sub)
                break  # We found it. Terminate the loop
        # Message body according to the roswebsocket v2 protocol
        req = {"op": "unsubscribe",
                "topic": topic}
        msg_str = json.dumps(req)  # Dictionary to json
        self.ws.send(msg_str)  # Send to server


    def advertise(self,topic,data_type):
        # This method is used to advertise to a topic
        # The following dictionary is according to ros bridge protocol
        found = False  # Initialization
        for this_pub in self.pubs:  # Loop through all existing publishing topics
            if this_pub['topic'] == topic:
                found = True
                break  # We found it. Terminate the loop
        if found == False:
            self.pubs.append({'topic':topic})
        # Message body according to the roswebsocket v2 protocol
        req={"op": "advertise",
        "topic": topic,
        "type":data_type
        }
        msg_str=json.dumps(req)  # Dictionary to json
        self.ws.send(msg_str)  # Send to server


    def publish(self, topic, data):
        # This method is used to publish a message
        msg_dict = {"data":data}
        # Message body according to the roswebsocket v2 protocol
        req={"op": "publish",
        "topic": topic,
        "msg" : msg_dict
        }
        msg_str=json.dumps(req)  # Dictionary to json
        self.ws.send(msg_str)  # Send to server

    def unadvertise(self, topic):
        # This method is used to unadvertise a topic
        for this_pub in self.pubs:  # Loop through all existing subscribed topics
            if this_pub['topic'] == topic:
                self.pubs.remove(this_pub)
                break  # We found it. Terminate the loop
        # Message body according to the roswebsocket v2 protocol
        req = {"op": "unadvertise",
                "topic": topic}
        msg_str = json.dumps(req)  # Dictionary to json
        self.ws.send(msg_str)  # Send to server










