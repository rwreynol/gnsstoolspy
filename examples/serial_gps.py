from gnss_stream import locosys_gnss, serial_gnss

import yaml
import time

def main():
    settings = None
    
    with open('settings.yaml','r') as file:
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

    time.sleep(10)

    gps.stop()
    gps.join()

if __name__ == '__main__':
    main()