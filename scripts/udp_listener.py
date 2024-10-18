import socket
import time

UDP_HOST = '0.0.0.0'
UDP_PORT = 1234
FILENAME = 'output.bin'

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)

    addr = (UDP_HOST,UDP_PORT)

    s.bind( addr )
    print('Listening at %s:%d' % addr)

    try:
        with open(FILENAME,'wb') as file:
            while True:
                try:
                    (msg,addr) = s.recvfrom(1024)
                    file.write(msg)
                    file.flush()
                    print(msg,addr)
                except:
                    time.sleep(0.5)
    except KeyboardInterrupt:
        print('User exiting')
