from positioning_outstream import positioning_file
from gnss_stream import serial_gnss

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
    file = positioning_file('out.txt')
    gnss.add_listener(file)
    
    gnss.start()

    time.sleep(10)

    gnss.stop()
    gnss.join()

    file.close()

if __name__ == '__main__':
    main()
