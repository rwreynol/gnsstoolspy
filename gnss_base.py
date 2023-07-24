from pyubx2 import UBXMessage
from math import trunc
from serial import Serial
import time

class BaseStation(object):
    _modes = ('SURVEY-IN','FIXED')
    _layer = 1 # 1 = RAM, 2 = BBR, 4 = Flash (can be OR'd)


    def __init__(self,gnss_type:str,rtcm_msgs:tuple,mode:str='fixed',conn:str='USB'):
        self.type = gnss_type
        self.ref = ()
        self._rtcm = rtcm_msgs
        self._conn_type = conn
        #print(gnss_type)
        #print('rtcm',self._rtcm,rtcm_msgs)
        #print(mode)
        #print(self._conn_type)

        if mode == 'fixed':
            print('Setting to fixed position')
            self._mode = 2
        elif mode == 'survey-in':
            print('Setting to survey-in')
            self._mode = 1
        else:
            print('Unrecognized mode. Setting to Survey In')
            self._mode = 1

    def configure(self,port:str,baud:float,lat:float,lon:float,alt:float,acc_limit:float,survey_min_s:float):
        '''
        Configure the gps
        '''
        rtcm_config_msg = self._setup(self._rtcm)

        if self._mode == 2:
            base_config_msg = self._fixed(lat,lon,alt,acc_limit)
        else:
            base_config_msg = self._survey_in(survey_min_s,acc_limit)

        with Serial(port,baud,timeout=1) as stream:
            print('Configuring the RTCM messages')
            self.send_msg(stream,rtcm_config_msg)
            time.sleep(0.1)
            print('Configuring the Base in %s' % self._modes[self._mode-1])
            self.send_msg(stream,base_config_msg)

    def send_msg(self,serial_out: Serial, ubx: UBXMessage):
        """
        Send config message to receiver.
        """

        print("Sending configuration message to receiver...")
        print(ubx)
        serial_out.write(ubx.serialize())

    def _setup(self,msgs) -> UBXMessage:
        print("\nFormatting RTCM MSGOUT CFG-VALSET message...")
        transaction = 0
        cfg_data = []
        #print(msgs)
        for rtcm_type in msgs:
            cfg = 'CFG_MSGOUT_RTCM_3X_TYPE%s_%s' % (rtcm_type,self._conn_type)
            #print(cfg)
            #cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{self._conn_type}"
            cfg_data.append([cfg, 1])

        return UBXMessage.config_set(self._layer, transaction, cfg_data)

    def _survey_in(self,svin_min_dur:float,acc_limit:float) -> UBXMessage:
        """
        Configure Survey-In mode with specied accuracy limit.
        """

        print("\nFormatting SVIN TMODE CFG-VALSET message...")
        transaction = 0
        acc_limit = int(round(acc_limit / 0.1, 0))
        cfg_data = [
            ("CFG_TMODE_MODE", 2),
            ("CFG_TMODE_SVIN_ACC_LIMIT", acc_limit),
            ("CFG_TMODE_SVIN_MIN_DUR", svin_min_dur),
            (f"CFG_MSGOUT_UBX_NAV_SVIN_{self._conn_type}", 1),
        ]

        return UBXMessage.config_set(self._layer, transaction, cfg_data)

    def _fixed(self,lat,lon,height,acc_limit) -> UBXMessage:
        """
        Configure Fixed mode with specified coordinates.
        """

        print("\nFormatting FIXED TMODE CFG-VALSET message...")
        pos_type = 1  # LLH (as opposed to ECEF)
        transaction = 0
        acc_limit = int(round(acc_limit / 0.1, 0))

        # separate standard and high precision parts of lat / lon
        # and apply scaling factors
        lat_7dp = trunc(lat * 1e7) / 1e7
        lat_hp = lat - lat_7dp
        lat = int(round(lat_7dp / 1e-7, 0))
        lat_hp = int(round(lat_hp / 1e-9, 0))
        lon_7dp = trunc(lon * 1e7) / 1e7
        lon_hp = lon - lon_7dp
        lon = int(round(lon_7dp / 1e-7, 0))
        lon_hp = int(round(lon_hp / 1e-9, 0))

        height = int(height)
        cfg_data = [
            ("CFG_TMODE_MODE", self._mode),
            ("CFG_TMODE_POS_TYPE", pos_type),
            ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
            ("CFG_TMODE_HEIGHT_HP", 0),
            ("CFG_TMODE_HEIGHT", height),
            ("CFG_TMODE_LAT", lat),
            ("CFG_TMODE_LAT_HP", lat_hp),
            ("CFG_TMODE_LON", lon),
            ("CFG_TMODE_LON_HP", lon_hp),
        ]

        return UBXMessage.config_set(self._layer, transaction, cfg_data)

class ZEDF9PBase(BaseStation):

    def __init__(self,mode:str='fixed',conn:str='USB'):
        super().__init__('ZED-F9P',# gps model
            ('1005','1077','1087','1097','1127','1230','4072_0','4072_1'), # rtcm messages
            mode,
            conn
            )
