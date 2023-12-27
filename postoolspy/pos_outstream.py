from .gnss_stream import gnss_interface
from .imu_stream import imu_interface
from .gnss_nmea import nmea_parser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import socket

class positiong_outstream(gnss_interface):
    '''
    positioning output stream object
    '''

    def __init__(self):
        ''' 
        constructor
        '''
        pass

class positioning_file(positiong_outstream):
    '''
    output file for positioning
    '''

    def __init__(self,filename):
        '''
        constructor for positioning output file
        '''
        self._name = filename
        self._file = open(self._name,'w')

    def new_imu(self,t,msg):
        '''
        handle new gnss message
        '''
        try:
            self._file.write( '%f %s' % (t,msg.decode()) )
        except Exception as e:
            print(str(e))

    def new_gnss(self,t,msg):
        '''
        handle new gnss message
        '''
        try:
            print('%f %s' % (t,msg.decode().strip()))
            self._file.write( '%f %s' % (t,msg.decode()) )
        except Exception as e:
            print(str(e))

    def close(self):
        '''
        closes the file
        '''
        self._file.close()

class udp_server(gnss_interface,imu_interface):

    def __init__(self,dest):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest = dest

    def new_imu(self,t,msg):
        msg = b'%.6f' % t + msg
        #print(msg,self.dest)
        self.sock.sendto(msg,self.dest)

    def new_gnss(self,t,msg):
        msg = b'%.6f' % t + msg
        print(msg,self.dest)
        self.sock.sendto(msg,self.dest)

    def close(self):
        self.sock.close()

class mavlink_server(gnss_interface,imu_interface):
    '''
    mission planner mavlink server replication object
    '''
    _file = 'mavlink'
    _gmsg = 'null'
    _imsg = 'null'
    _gtime = 0
    _itime = 0

    def __init__(self,address):
        '''
        constructor
        '''
        self._gtime = 0
        self._itime = self._gtime
        self.write()
        self._addr = address
        self._nparse = nmea_parser()
        
    def new_gnss(self,t,msg):
        '''
        handles new gnss
        '''
        try:
            parsed = self._nparse.parse(msg.decode())
            self._gtime = t * 1e6
            self._gmsg = {'time_usec':parsed.time*1e6,
                        'lat':parsed.lat*1e7,
                        'lon':parsed.lon*1e7,
                        'alt':parsed.lat*1e3,
                        'eph':9999,
                        'epv':9999,
                        'cog':0,
                        'fix_type':parsed.quality,
                        'satellites_visible':parsed.numSV,
                        'alt_ellipsoid':0,
                        'h_acc':0,
                        'v_acc':0,
                        'vel_acc':0,
                        'yaw':0}
        except Exception as e:
            print(self.__class__.__name__,str(e))

        # write message to string
        self.write()

    def new_imu(self,t,msg):
        try:
            parsed = self._nparse.parse(msg.decode())
            #print(t,parsed)
            self._itime = t * 1e6
            self._imsg = {'time_usec':0,
                        'yaw':parsed.yaw,
                        'pitch':parsed.pitch,
                        'roll':parsed.roll,}
        except Exception as e:
            print(self.__class__.__name__,str(e))

        self.write()

        
    def write(self):
        '''
        writes the gnss and imu data to local json file
        '''
        t = time.time()# computer timestamp
        if t - self._gtime > 1:
            self._gmsg = 'null'
        if t- self._itime > 1:
            self._imsg = 'null'
        j = json.dumps({'GPS_RAW_INT':{'msg':self._gmsg,'index':1,'time_usec':self._gtime*1e6},
                        'ATTITUDE':{'msg':self._imsg,'index':1,'time_usec':self._itime*1e6} })
        
        # write file
        with open(self._file + '.json','w') as file:
            file.write(j)
        
    def run(self):
        '''
        server thread
        '''
        http = HTTPServer( self._addr, mavlink_server_request)

        try:
            http.serve_forever()
        except KeyboardInterrupt:
            print('User terminated Webserver')

class mavlink_server_request(BaseHTTPRequestHandler):
    '''
    server request override
    '''

    def do_GET(self):
        '''
        handles get response
        '''
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        resp = 'unknown'

        if self.path == '/mavlink':
            with open('mavlink.json','r') as file:
                resp = file.read()
            
        self.wfile.write(bytes("<html><head><title>Simulated Mission Planner Webserver</title></head>", "utf-8"))
        self.wfile.write(bytes(resp, "utf-8"))