from threading import Thread
from pyubx2 import UBXReader
from gnss_corrections import corrections_interface

import math

import serial
import time

class gnss_interface(object):

    def new_gnss(self,t,msg):
        pass

class gnss(Thread,corrections_interface):

    def __init__(self):
        super().__init__()
        self._conn = None
        self._connected = False
        self._listeners = []

    def add_listener(self,listener):
        self._listeners.append(listener)

    def send_gnss(self,t,msg):
        for l in self._listeners:
            l.new_gnss(t,msg)

    def new_rtcm(self,msg):
        self.write(msg)

    def connect(self):
        pass

    def write(self,msg):
        pass

    def disconnect(self):
        pass

    def receive(self):
        pass

    def setup(self):
        pass

    def stop(self):
        self._connected = False
        print('Stopping the stream')

    def run(self):
        self.connect()

        self.setup()

        while self._connected:
            (t,msg) = self.receive()

            if msg is not None:
                self.send_gnss(t,msg)

        self.disconnect()
            
class serial_gnss(gnss):

    def __init__(self,port,baud):
        super().__init__()
        self._port = port
        self._baud = baud

    def setup(self):
        self._parser = UBXReader(self._conn,protfilter=1)
        
    def connect(self):
        try:
            self._conn = serial.Serial(self._port,self._baud)
            self._connected = True
            print('Connected to (%s:%d)' % (self._port,self._baud))
        except Exception as e:
            print(str(e))
            print('Error connecting to serial gps')
            self._connected = False

    def disconnect(self):
        try:
            self._conn.close()
            self._conn = None
            print('Disconnected from gnss stream')
        except Exception:
            print('Error closing serial gps')

        self._connected = False

    def receive(self):
        try:
            (raw,msg) = self._parser.read()
            t = time.time()
            if msg.msgID == 'GGA':
                print(raw)
                if not msg.lat:
                    return (t,raw)#(time.time(),msg.time,math.nan,math.nan,math.nan,msg.quality,0)
                return (t,raw)#(time.time(),msg.time,msg.lat,msg.lon,msg.alt,msg.quality,msg.numSV)
            else:
                return (t,None)
        except Exception as e:
            print(self.__class__.__name__ + ' ' + str(e))
            return (None,None)
        
    def write(self,msg):
        try:
            self._conn.write(msg)
            print('Writing RTCM data to serial port')
        except Exception as e:
            print(self.__class__.__name__ + ' ' + str(e))

    def checksum(self,string):
        csum = 0
        for s in string:
            csum = csum ^ ord(s)
        return csum

class locosys_gnss(serial_gnss):

    def setup(self):

        cmds = ['PAIR410,1', # enable SBAS
                'PAIR400,1', # DGPS = RTCM
                'PAIR104,1', # dual band
                'PAIR050,100'# 10Hz
                ]
        
        for cmd in cmds:
            string = '$%s*%X\r\n' % (cmd,self.checksum(cmd))
            self._conn.flush()
            self._conn.write(string.encode('utf-8'))
            line = self._conn.readline().decode('utf-8').strip()
            print(string,line)

        super().setup()

    def write(self,msg):
        super().write(msg + b'\r\n')