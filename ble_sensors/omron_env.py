# coding: UTF-8
from bluepy import btle
import struct

#Broadcastデータ取得用デリゲート
class OmronBroadcastScanDelegate(btle.DefaultDelegate):
    #コンストラクタ
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        #センサデータ保持用変数
        self.sensorValue = None

    # スキャンハンドラー
    def handleDiscovery(self, dev, isNewDev, isNewData):  
        # 新しいデバイスが見つかったら
        if isNewDev or isNewData:  
            # アドバタイズデータを取り出し
            for (adtype, desc, value) in dev.getScanData():  
                #環境センサのとき、データ取り出しを実行
                if desc == 'Manufacturer' and value[0:4] == 'd502':
                    #センサの種類（EP or IM）を取り出し
                    sensorType = dev.scanData[dev.SHORT_LOCAL_NAME].decode(encoding='utf-8')
                    #EPのときのセンサデータ取り出し
                    if sensorType == 'EP':
                        self._decodeSensorData_EP(value)
                    #IMのときのセンサデータ取り出し
                    if sensorType == 'IM':
                        self._decodeSensorData_IM(value)

    # センサデータを取り出してdict形式に変換（EPモード時）
    def _decodeSensorData_EP(self, valueStr):
        #文字列からセンサデータ(6文字目以降)のみ取り出し、バイナリに変換
        valueBinary = bytes.fromhex(valueStr[6:])
        #バイナリ形式のセンサデータを整数型Tapleに変換
        (temp, humid, light, uv, press, noise, discomf, wbgt, rfu, batt) = struct.unpack('<hhhhhhhhhB', valueBinary)
        #単位変換した上でdict型に格納
        self.sensorValue = {
            'SensorType': 'Omron_BAG_EP',
            'Temperature': temp / 100,
            'Humidity': humid / 100,
            'Light': light,
            'UV': uv / 100,
            'Pressure': press / 10,
            'Noise': noise / 100,
            'Discomfort': discomf / 100,
            'WBGT': wbgt / 100,
            'BatteryVoltage': (batt + 100) / 100
        }
    
    # センサデータを取り出してdict形式に変換（IMモード時）
    def _decodeSensorData_IM(self, valueStr):
        #文字列からセンサデータ(6文字目以降)のみ取り出し、バイナリに変換
        valueBinary = bytes.fromhex(valueStr[6:])
        #バイナリ形式のセンサデータを整数型Tapleに変換
        (temp, humid, light, uv, press, noise, accelX, accelY, accelZ, batt) = struct.unpack('<hhhhhhhhhB', valueBinary)
        #単位変換した上でdict型に格納
        self.sensorValue = {
            'SensorType': 'Omron_BAG_IM',
            'Temperature': temp / 100,
            'Humidity': humid / 100,
            'Light': light,
            'UV': uv / 100,
            'Pressure': press / 10,
            'Noise': noise / 100,
            'AccelerationX': accelX / 10,
            'AccelerationY': accelY / 10,
            'AccelerationZ': accelZ / 10,
            'BatteryVoltage': (batt + 100) / 100
        }

#Connectモードデータ取得クラス
class GetOmronConnectModeData():
    def get_env_usb_data(self, macaddr):
        peripheral = btle.Peripheral(macaddr, addrType=btle.ADDR_TYPE_RANDOM)
        characteristic = peripheral.readCharacteristic(0x0059)
        return self._decodeSensorData_EP(characteristic)

    def _decodeSensorData_EP(self, valueBinary):
        (seq, temp, humid, light, press, noise, eTVOC, eCO2) = struct.unpack('<Bhhhlhhh', valueBinary)
        sensorValue = {
                'SensorType': 'Omron_USB_EP',
                'Temperature': temp / 100,
                'Humidity': humid / 100,
                'Light': light,
                'Pressure': press / 1000,
                'Noise': noise / 100,
                'eTVOC': eTVOC,
                'eCO2': eCO2
            }
        return sensorValue