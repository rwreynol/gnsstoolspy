from postoolspy.gnss_ntrip import ntrip_server, ntrip_handler
from postoolspy.gnss_corrections import ntrip_corrections

import yaml

def main():

    settings = None

    with open('settings.yaml','r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings is None: 
        print('error reading settings file')
        return
    
    addr = (settings['server']['address'],settings['server']['port'])
    server = ntrip_server('randall;',
                          'password',
                          'WRJ',
                          (settings['server']['lat'],settings['server']['lon']),
                           1,addr,ntrip_handler)
    
    gnss_cors = ntrip_corrections('127.0.0.1',
                                  'WRJ',
                                  'randall',
                                  'password',
                                  2101,
                                  org='EMSG')
    gnss_cors.start()

    try:
        server.serve_forever()        
    except KeyboardInterrupt:
        print('User Teminating Server')
    
    gnss_cors.stop()
    gnss_cors.join()

    server.server_close()

if __name__ == '__main__':
    main()