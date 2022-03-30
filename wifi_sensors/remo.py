import json
import requests
import glob
import pandas as pd

#Remoデータ取得クラス
class GetRemoData():
    def get_sensor_data(self, Token, API_URL):
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + Token,
        }
        response = requests.get(f"{API_URL}/1/devices", headers=headers)
        rjson = response.json()
        return self._decodeSensorData(rjson)

    def get_aircon_power_data(self, Token, API_URL):
        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + Token,
        }
        response = requests.get(f"{API_URL}/1/appliances", headers=headers)
        rjson = response.json()
        return self._decodeAirconPowerData(rjson)

    def calc_human_motion(self, Human_last, csvdir):
        filelist = glob.glob(f"{csvdir}/*/*.csv")
        if len(filelist) == 0:
            return 0
        filelist.sort()
        df = pd.read_csv(filelist[-1])
        if df.Human_last[len(df) - 1] != Human_last:
            return 1
        else:
            return 0

    # センサデータを取り出してdict形式に変換
    def _decodeSensorData(self, rjson):
        for device in rjson:
            #Remoのデータ
            if device['firmware_version'].split('/')[0] == 'Remo':
                sensorValue = {
                    'SensorType': 'Remo_Sensor',
                    'Temperature': device['newest_events']['te']['val'],
                    'Humidity': device['newest_events']['hu']['val'],
                    'Light': device['newest_events']['il']['val'],
                    'Human_last': device['newest_events']['mo']['created_at']
                }
        return sensorValue

    # エアコンおよび電力データを取り出してdict形式に変換
    def _decodeAirconPowerData(self, rjson):
        Value = {}
        for appliance in rjson:
            #エアコン
            if appliance['type'] == 'AC':
                Value['TempSetting'] = appliance['settings']['temp']
                Value['Mode'] = appliance['settings']['mode']
                Value['AirVolume'] = appliance['settings']['vol']
                Value['AirDirection'] = appliance['settings']['dir']
                Value['Power'] = appliance['settings']['button']
            #スマートメータの電力データ
            elif appliance['type'] == 'EL_SMART_METER':
                for meterValue in appliance['smart_meter']['echonetlite_properties']:
                    if meterValue['name'] == 'normal_direction_cumulative_electric_energy':
                        Value['CumulativeEnergy'] = float(meterValue['val'])/100
                    elif meterValue['name'] == 'measured_instantaneous':
                        Value['Watt'] = int(meterValue['val'])        
        #値を取得できていないとき、Noneとする
        if len(Value) == 0:
            Value = None
        return Value