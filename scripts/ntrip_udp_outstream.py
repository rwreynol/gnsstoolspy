from postoolspy.gnss_corrections import ntrip_corrections, rtcm_udpcast

import yaml
import time

def main():

    with open('ntrip.yaml','r') as stream:
        settings = yaml.safe_load(stream)

        udp_serv = rtcm_udpcast(settings['broadcaster']['connection']['destination'],
                                settings['broadcaster']['connection']['port'])

        gnss_cors = ntrip_corrections(settings['corrections']['connection']['host'],
                                  settings['corrections']['connection']['mountpoint'],
                                  settings['corrections']['connection']['user'],
                                  settings['corrections']['connection']['password'],
                                  settings['corrections']['connection']['port'],
                                  org='EMSG')
        #print(settings)
        
        gnss_cors.add_listener(udp_serv)
        
        gnss_cors.start()

        time.sleep(10)

        gnss_cors.stop()
        gnss_cors.join()

        udp_serv.close()

        
    

if __name__ == '__main__':
    main()