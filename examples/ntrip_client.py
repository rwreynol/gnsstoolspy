from postoolspy.gnss_corrections import ntrip_corrections

import time
import yaml

def main():

    settings = None

    with open('settings.yaml','r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings is None: 
        print('error reading settings file')
        return
    
    gnss_cors = ntrip_corrections(settings['corrections']['connection']['address'],
                                  settings['corrections']['connection']['mountpoint'],
                                  settings['corrections']['connection']['user'],
                                  settings['corrections']['connection']['password'],
                                  settings['corrections']['connection']['port'],
                                  org='EMSG')
    gnss_cors.start()
    time.sleep(10)

    gnss_cors.stop()

if __name__ == '__main__':
    main()