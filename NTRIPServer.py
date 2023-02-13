import yaml
import os
import BaseStation

# available settings for the script
CONNS = ['USB','UART1','UART2']
MODES = ['fixed','survey-in']

def main():
    '''
    '''
    # program the gnss from settings
    file = os.path.join(os.path.curdir(),'settings.yaml')
    success = False
    with open(file,'r') as f:
        settings = yaml.load(f.read())
        print('imported settings')

        if settings['gnss']['port']['type'] not in CONNS:
            print('Connection type is not recognized')
        elif settings['monument']['type'] not in MODES:
            print('Mode is not recognized')

        if settings['gnss']['type'] == 'zed-f9p':
            base = BaseStation.ZEDF9PBase()
        else:
            print('GPS type is not recognized')
            return

        # connect and program the base
        base.configure()

        sucess = True

    if sucess:
        print('Setting up the ntrip server')
        print('Needs to be implement')

if __name__ == '__main__':
    main()