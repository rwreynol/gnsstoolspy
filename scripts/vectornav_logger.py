from postoolspy.imu_stream import vectornav_imu
from postoolspy.pos_outstream import udp_server
import time
import yaml
import sys
import os

def main():
        
    settings = None

    file = os.path.join(os.path.dirname(__file__),'settings.yaml')
        
    with open(file,'r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings == None:
        sys.exit(1)

    port = settings['imu']['connection']['port']
    baud = settings['imu']['connection']['baud']

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

if __name__ == '__main__':
    main()


#serv.close()


imu.join()