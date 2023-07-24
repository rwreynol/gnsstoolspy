from threading import Thread

import socket
import base64

class corrections_interface(object):

    def new_rtcm(self):
        pass

class gnss_corrections(Thread):

    def __init__(self):
        super().__init__()
        self._conn = None
        self._connected = False
        self._listeners = []

    def add_listener(self,listener):
        self._listeners.append(listener)

    def send_rtcm(self,msg):
        for l in self._listeners:
            l.new_rtcm(msg)

    def connect(self):
        pass

    def receive(self):
        pass

    def disconnect(self):
        self._conn = None

    def stop(self):
        self._connected = False

    def run(self):

        self.connect()

        print('Connected: %s' % str(self._connected))

        while self._connected:
            msg = self.receive()
            self.send_rtcm(msg)

        self.disconnect()

    def new_rtcm(self):
        pass

class ntrip_corrections(gnss_corrections):
    ENCODING = 'ascii'

    def __init__(self,host,mountpoint,user,password,port=2101,org=''):
        super().__init__()
        self._header = self.get_header(host,mountpoint,user,password,port,org).encode(self.ENCODING)
        self._source = self.sourcetable(host,mountpoint,user,password,port,org).encode(self.ENCODING)

        self._addr = (host,port)

    def sourcetable(self,host,mount,user,password,port,org):
        return ('GET / HTTP/1.0\r\n' +
                'Host: %s:%d\r\n' +
                'User-Agent: NTRIP RTk GPS Tools/1.0\r\n' +
                'Accept: */*\r\n' +
                '\r\n') % (host, port)

    def get_header(self,host,mount,user,password,port,org):
        user = base64.b64encode(('%s:%s'%(user,password)).encode(encoding=self.ENCODING))
        return 'GET /%s HTTP/1.1\r\n' % mount +\
            'Host: %s:%d\r\n' % (host,port) +\
            'Ntrip-Version: Ntrip/2.0\r\n' +\
            'User-Agent: NTRIP RTk GPS Tools/1.0\r\n' +\
            'Authorization: Basic %s\r\n' % (user.decode(encoding=self.ENCODING)) +\
            'Connection: close\r\n\r\n'
    
    def connect(self):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect(self._addr)
        self._conn.send(self._header)
        resp = self.receive().decode(self.ENCODING)
        print(resp)

        for line in resp.split():
            if 'OK' in line:
                self._connected = True
                break

    def receive(self):
        if self._conn is not None:
            return self._conn.recv(2048)
        else: return None

    def disconnect(self):
        self._conn.close()
        print('Closed %s' % str(self._addr))
        super().__init__()