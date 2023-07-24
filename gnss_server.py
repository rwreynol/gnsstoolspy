from datetime import datetime, timezone

from socketserver import StreamRequestHandler, ThreadingTCPServer

class NTRIPServer(ThreadingTCPServer):
    nclients = 0

    def __init__(self,credentials,position,maxclients=1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.max_clients = maxclients
        self._credentials = credentials
        self._pos = position

class NTRIPHandler(StreamRequestHandler):
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
            f"HTTP/1.1 {code} {codes[code]}\r\n"
            + "Ntrip-Version: Ntrip/2.0\r\n"
            + "Ntrip-Flags: \r\n"
            + f"Server: pygnssutils_NTRIP_Caster_{VERSION}/of:{server_date}\r\n"
            + f"Date: {http_date}\r\n"
        )
        return header

    def sourcetable(self):
        PYGPSMP = ''
        ipaddr=''
        port=''
        lat=''
        lon=''
        sourcetable = (
            f"STR;{PYGPSMP};PYGNSSUTILS;RTCM 3.3;"
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
        pass

    def handle(self):
        """
        Overridden main client handler.

        If in NTRIP server mode, will respond to NTRIP client authentication
        and sourcetable requests and, if valid, stream relevant RTCM3 data
        from the input message queue to the socket.

        If in open socket server mode, will simply stream content of
        input message queue to the socket.
        """
        data = self.request.recv(1024).strip()
        print(data)

if __name__ == '__main__':
    addr = ('0.0.0.0',8080)
    server = NTRIPServer('',(0,0),1,addr,NTRIPHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('User Teminating Server')
        server.server_close()