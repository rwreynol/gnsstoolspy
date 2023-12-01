from postoolspy.gnss_stream import locosys_gnss, serial_gnss

import yaml
import time
import os

def main():
    settings = None

    file = os.path.join(os.path.dirname(__file__),'settings.yaml')
    
    with open(file,'r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings is None:
        print('error reading settings')
        return 0
    
    gps = locosys_gnss(port=settings['gnss']['connection']['port'],
                      baud=settings['gnss']['connection']['baud'])
    #gps = serial_gnss(port=settings['gnss']['connection']['port'],
    #                  baud=settings['gnss']['connection']['baud'])
    
    gps.start()

    time.sleep(1)

    gps.stop()
    gps.join()

if __name__ == '__main__':
    main()