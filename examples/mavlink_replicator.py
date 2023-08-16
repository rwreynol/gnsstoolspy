from postoolspy.pos_outstream import mavlink_server
from postoolspy.gnss_stream import serial_gnss

import time
import yaml

def main():
    settings = None
    
    with open('settings.yaml','r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings is None:
        print('error reading settings')
        return 0
    
    gnss = serial_gnss(settings['gnss']['connection']['port'],
                       settings['gnss']['connection']['baud'])
    serv = mavlink_server( ('0.0.0.0',56781) )
    gnss.add_listener(serv)
    
    gnss.start()

    serv.run()

    gnss.stop()
    gnss.join()

    file.close()

if __name__ == '__main__':
    main()
