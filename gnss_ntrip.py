from datetime import datetime, timezone

from socketserver import StreamRequestHandler, ThreadingTCPServer

import base64

class ntrip_server(ThreadingTCPServer):
    nclients = 0

    def __init__(self,usr,pw,mountpoint,position,maxclients=1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.max_clients = maxclients
        self.credentials = self.credentials(usr,pw)
        self._pos = position
        self.mountpoint = mountpoint

    def credentials(self,user,password):
        creds = user + ':' + password
        return base64.b64encode(creds.encode('ascii')).decode('ascii')

class ntrip_handler(StreamRequestHandler):
    codes = {
            200: "OK",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)

    def header(self,code):
        dat = datetime.now(timezone.utc)
        server_date = dat.strftime("%d %b %Y")
        http_date = dat.strftime("%a, %d %b %Y %H:%M:%S %Z")
        VERSION = '2.0'
        header = (
            f"HTTP/1.1 {code} {self.codes[code]}\r\n"
            + "Ntrip-Version: Ntrip/2.0\r\n"
            + "Ntrip-Flags: \r\n"
            + f"Server: pygnssutils_NTRIP_Caster_{VERSION}/of:{server_date}\r\n"
            + f"Date: {http_date}\r\n"
        )
        return header

    def sourcetable(self):
        ipaddr='127.0.0.1'
        port=2101
        lat=43
        lon=-72
        sourcetable = (
            f"STR;RTKGPSTOOLS;CRREL;RTCM 3.3;"
            + "1005(5),1077(1),1087(1),1097(1),1127(1),1230(1);"
            + f"0;GPS+GLO+GAL+BEI;SNIP;SRB;{lat};{lon};0;0;sNTRIP;none;B;N;0;\r\n"
        )
        sourcefooter = (
            f"NET;SNIP;pygnssutils;N;N;pygnssutils;{ipaddr}:{port};info@semuconsulting.com;;\r\n"
            + "ENDSOURCETABLE\r\n"
        )
        
        return ("Content-Type: gnss/sourcetable\r\n" +
                + f"Content-Length: {len(sourcetable) + len(sourcefooter)}\r\n" +
                sourcetable+sourcefooter
                )

    def response(self):
        return self.header(400) + ('Connection: close\r\n' + 
                'Transfer-Encoding: chunked\r\n' +
                'Content-Type: gnss/data\r\n'+
                'Cache-Control: no-store\r\n'
                'Pragma: no-cache\r\n\r\n')

    def handle(self):
        data = self.request.recv(1024).decode('ascii').splitlines()
        print("Recieved one request from {}".format(self.client_address[0]))

        print(dir(self))

        for line in data:
            print(line)
            if line.startswith('GET'):
                parts = line.split()
                if parts[1] == '/':
                    print('source table')
                elif parts[1] == '/' + self.server.mountpoint:
                    print('selected proper mount point')
                else:
                    print('error. incorrect mount point')
            elif line.startswith('Authorization: Basic'):
                print(line)
                parts = line.split()
                if parts[2] == self.server.credentials:
                    print('authorized')
                else:
                    print('unauthorized')
                    print(self.server.credentials)

        print(data)

