from threading import Thread
from pyubx2 import UBXReader

import math

import serial
import time

class gnss_interface(object):

    def new_gnss(self):
        pass

class gnss(Thread):

    def __init__(self):
        super().__init__()
        self._conn = None
        self._connected = False
        self._listeners = []

    def add_listener(self,listener):
        self._listeners.append(listener)

    def send_gnss(self,msg):
        for l in self._listeners:
            l.new_gnss(msg)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def receive(self):
        pass

    def stop(self):
        self._connected = False
        print('Stopping the stream')

    def run(self):
        self.connect()

        while self._connected:
            msg = self.receive()

            if msg is not None:
                self.send_gnss(msg)
                print(msg)

        self.disconnect()
            

class serial_gnss(gnss):

    def __init__(self,port,baud):
        super().__init__()
        self._port = port
        self._baud = baud
        
    def connect(self):
        try:
            self._conn = serial.Serial(self._port,self._baud)
            self._parser = UBXReader(self._conn,protfilter=1)
            self._connected = True
            print('Connected to (%s:%d)' % (self._port,self._baud))
        except Exception as e:
            print(str(e))
            print('Error connecting to serial gps')
            self._connected = False

    def disconnect(self):
        try:
            self._conn.close()
            print('Disconnected from gnss stream')
        except Exception:
            print('Error closing serial gps')

        self._connected = False

    def receive(self):
        try:
            (_,msg) = self._parser.read()
            if msg.msgID == 'GGA':
                if not msg.lat:
                    return (time.time(),msg.time,math.nan,math.nan,math.nan,msg.quality,0)
                return (time.time(),msg.time,msg.lat,msg.lon,msg.alt,msg.quality,msg.NS)
            else:
                return None
        except Exception as e:
            print(str(e))
            print('error reading serial gps')
            return None