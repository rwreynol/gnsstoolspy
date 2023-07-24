from gnss_stream import gnss_interface
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

class positiong_outstream(gnss_interface):

    def __init__(self):
        pass

class positioning_file(gnss_interface):

    def __init__(self,filename):
        self._name = filename

        self._file = open(self._name,'w')
        self._file.write('cpu_time,timestamp,lat_deg,lon_deg,alt_m,fix,num_sats\r\n')

    def new_gnss(self,msg):
        try:
            self._file.write( ('%f,%s,%f,%f,%f,%d,%d\r\n' % msg) )
        except Exception as e:
            print(str(e))
            print(msg)

    def close(self):
        self._file.close()

class mavlink_server(gnss_interface):
    _file = 'mavlink'
    _gmsg = 'null'
    _imsg = 'null'
    _gtime = 0
    _itime = 0

    def __init__(self,address):
        self._gtime = 0
        self._itime = self._gtime
        self.write()
        self._addr = address
        
    def new_gnss(self,msg):
        self._gtime = time.time() * 1e6
        self._gmsg = {'time_usec':msg[0]*1e6,
                      'lat':msg[2]*1e7,
                      'lon':msg[3]*1e7,
                      'alt':msg[4]*1e3,
                      'eph':9999,
                      'epv':9999,
                      'cog':0,
                      'fix_type':msg[5],
                      'satellites_visible':msg[6],
                      'alt_ellipsoid':0,
                      'h_acc':0,
                      'v_acc':0,
                      'vel_acc':0,
                      'yaw':0}

    def write(self):
        t = time.time()
        if t - self._gtime > 1:
            self._gmsg = 'null'
        if t- self._itime > 1:
            self._imsg = 'null'
        j = json.dumps({'GPS_RAW_INT':{'msg':self._gmsg},
                        'ATTITUDE':{'msg':self._imsg} })

        with open(self._file + '.json','w') as file:
            file.write(j)
        
    def run(self):
        http = HTTPServer( self._addr, mavlink_server_request)

        try:
            http.serve_forever()
        except KeyboardInterrupt:
            print('User terminated Webserver')

class mavlink_server_request(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        resp = 'unknown'

        if self.path == '/mavlink':
            with open('mavlink.json','r') as file:
                resp = file.read()
            
        self.wfile.write(bytes("<html><head><title>Simulated Mission Planner Webserver</title></head>", "utf-8"))
        self.wfile.write(bytes(resp, "utf-8"))

if __name__ == '__main__':
    serv = mavlink_server(('0.0.0.0',56781))
    serv.run()