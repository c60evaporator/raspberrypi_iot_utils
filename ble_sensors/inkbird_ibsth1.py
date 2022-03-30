from bluepy import btle
import struct

#Inkbird IBS-TH1データ取得クラス
class GetIBSTH1Data():
    def get_ibsth1_data(self, macaddr, sensortype):
        #デバイスに接続
        peripheral = btle.Peripheral(macaddr)
        #IBS-TH1 miniのとき
        if sensortype == 'Inkbird_IBSTH1mini':
            characteristic = peripheral.readCharacteristic(0x002d)
            return self._decodeSensorData_mini(characteristic)
        #IBS-TH1のとき
        elif sensortype == 'Inkbird_IBSTH1':
            characteristic = peripheral.readCharacteristic(0x28)
            return self._decodeSensorData(characteristic)
        else:
            return None
    
    #IBS-TH1 mini
    def _decodeSensorData_mini(self, valueBinary):
        (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', valueBinary)
        sensorValue = {
                'SensorType': 'Inkbird_IBSTH1mini',
                'Temperature': temp / 100,
                'Humidity': humid / 100,
                'unknown1': unknown1,
                'unknown2': unknown2,
                'unknown3': unknown3,
            }
        return sensorValue

    #IBS-TH1
    def _decodeSensorData(self, valueBinary):
        (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', valueBinary)
        sensorValue = {
                'SensorType': 'Inkbird_IBSTH1',
                'Temperature': temp / 100,
                'Humidity': humid / 100,
                'unknown1': unknown1,
                'unknown2': unknown2,
                'unknown3': unknown3,
            }
        return sensorValue