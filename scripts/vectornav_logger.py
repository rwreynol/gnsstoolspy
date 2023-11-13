from postoolspy.imu_stream import vectornav_imu
from postoolspy.pos_outstream import udp_server
import time
import yaml
import sys
port = 'COM3'
baud = 115200

settings = None
    
with open('settings.yaml','r') as file:
    settings = yaml.safe_load(file)
    print(settings)

if settings == None:
    sys.exit(1)

imu = vectornav_imu(port,baud)
imu.start()

dest = ('127.0.0.1',56781) 
serv = udp_server( dest )
imu.add_listener(serv)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

imu.stop()


#serv.close()


imu.join()