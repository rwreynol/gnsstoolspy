import re

class nmea_parser:

    def checksum(self,string):
        msg = re.findall(r'\$(.*?)\*',string)[0]
        csum = 0
        for s in msg:
            csum = csum ^ ord(s)
        return '%X' % csum

    def parse(self,string):
        try:
            msgid = re.findall(r'\$(.*?),',string)[0]
            chksm = re.findall(r'\*(.*?)\s',string)[0]
            calc_chksm = self.checksum(string)

            if chksm != calc_chksm:
                print('Checksums dont match')
                return nmea_result()  
            elif bool(re.search(r'G[NPL]GGA',msgid)):# parse gga string
                return self._parse_gga(string)
            else:
                print('Unknown NMEA identifier')
                return nmea_result()
            
        except Exception as e:
            print(str(e))
            return nmea_result()

    def _parse_gga(self,string):
        info = re.split(r',',string.strip())
        t = self._parse_time(info[1])
        lat = self._parse_lat(info[2],info[3])
        lon = self._parse_lon(info[4],info[5])
        quality = float(info[6])
        numSV = float(info[7])
        alt = float(info[9])

        return nmea_result(identity='GGA',time=t,lat=lat,lon=lon,quality=quality,numSV=numSV,alt=alt)

    def _parse_time(self,str_time):
        t = re.split(r'\.',str_time)
        t_gps = float(t[0][0:2])*3600 + float(t[0][2:4]) * 60 + float(t[0][4:]) + .001*float(t[1])
        return t_gps
    
    def _parse_lat(self,str_lat,dir_lat):
        l = re.split(r'\.',str_lat)
        lat = float(l[0][0:-2]) + float(l[0][-2:] + '.' + l[1])/60.0

        if dir_lat == 'S': lat *= -1
        return lat
    
    def _parse_lon(self,str_lon,dir_lon):
        l = re.split(r'\.',str_lon)
        lon = float(l[0][0:-2]) + float(l[0][-2:] + '.' + l[1])/60.0

        if dir_lon == 'W': lon *= -1
        return lon

    def _parse_gga_slam(self,string):
        pass

class nmea_result(object):

    msg_id = 'none'

    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return str(self.__dict__)

if __name__ == '__main__':
    msg = b'$GNGGA,133700.000,4343.4719600,N,07216.3614200,W,1,23,0.76,167.40,M,-32.58,M,,*4E\r\n'
    msg = msg.decode()

    nparser = nmea_parser()

    print(nparser.parse(msg))
