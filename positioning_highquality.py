from positioning_outstream import positioning_file
from gnss_stream import serial_gnss
from gnss_corrections import ntrip_corrections

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
    
    # initialize all objects
    rtcm = ntrip_corrections(settings['corrections']['connection']['address'],
                            settings['corrections']['connection']['mountpoint'],
                            settings['corrections']['connection']['user'],
                            settings['corrections']['connection']['password'],
                            settings['corrections']['connection']['port'],
                            org='EMSG')
    
    gnss = serial_gnss(settings['gnss']['connection']['port'],
                       settings['gnss']['connection']['baud'])
    
    file = positioning_file('out.txt')

    # add listeners for rtcm and gps data
    rtcm.add_listener(gnss)
    gnss.add_listener(file)
    
    # start the threads
    rtcm.start()
    gnss.start()

    # wait for 10 seconds
    time.sleep(10)

    # stop all threads
    gnss.stop()
    rtcm.stop()

    # wait for all threads to stop and close file
    if gnss.is_alive(): gnss.join()
    if rtcm.is_alive(): rtcm.join()
    file.close()

if __name__ == '__main__':
    main()
