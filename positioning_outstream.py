from gnss_stream import gnss_interface
from threading import Thread

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

            