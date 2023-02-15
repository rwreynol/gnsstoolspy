import yaml
import os
import time

import BaseStation

from pygnssutils.gnssserver import GNSSSocketServer


# available settings for the script
CONNS = ['USB','UART1','UART2']
MODES = ['fixed','survey-in']

def main():
    '''
    '''
    # program the gnss from settings
    file = os.path.join(os.curdir,'settings.yaml')
    success = False
    with open(file,'r') as f:
        settings = yaml.safe_load(f.read())
        print('imported settings')

        if settings['gnss']['port']['type'] not in CONNS:
            print('Connection type is not recognized')
        elif settings['monument']['type'] not in MODES:
            print('Mode is not recognized')

        if settings['gnss']['type'] == 'zed-f9p':
            base = BaseStation.ZEDF9PBase()#settings['monument']['type'],
                    #settings['gnss']['port']['type'])
        else:
            print('GPS type is not recognized')
            return

        # connect and program the base
        base.configure(settings['gnss']['port']['name'],
                settings['gnss']['port']['baud'],
                settings['monument']['lat'],
                settings['monument']['lon'],
                settings['monument']['alt'],
                settings['monument']['acc'],
                settings['monument']['duration'])

        sucess = True

    if sucess:
        print('Setting up the ntrip server')
        try:
            args = {
                    'app': None,
                    'inport': settings['gnss']['port']['name'],
                    'baudrate': settings['gnss']['port']['baud'],
                    'hostip':'0.0.0.0',
                    'outport':settings['ntrip']['port'],
                    #'maxclients':4,
                    'ntripmode':1,
                    #'validate':1,
                    #'parsebitfield':1,
                    #'format':1,
                    'profilter':4,
                    'verbosity':3
                    }

            with GNSSSocketServer(**args) as server:
                ready = server.run()

                while ready:
                    time.sleep(0.01)
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
