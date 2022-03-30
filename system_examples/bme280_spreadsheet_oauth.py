from datetime import datetime
import yaml

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gpio_sensors.bme280 import GetBme280
from google_scripts.run_script_oauth import RunScriptOAuth

RETRY = 5  # センサ取得繰り返し回数

###### BME280センサデータの取得 ######
bme = GetBme280()
temp, pres, hum = 0.0, 0.0, 0.0
#データ値が得られないとき、最大RETRY回取得を繰り返す
for i in range(RETRY):
    try:
        temp, pres, hum = bme.readData()
        print(f'temperature={temp}')
        print(f'pressure={pres}')
        print(f'humidity={hum}')
    #エラー出たら再度実行
    except:
        continue
    else:
        break

###### スプレッドシートへデータ送信 ######
with open('./google_scripts/google_creds/google_creds.yaml', encoding='utf-8_sig') as f:
    config=yaml.safe_load(f)
# スクリプト実行用クラスのインスタンス生成
google_script = RunScriptOAuth(client_secrets_path=config['client_secrets_path'],
                                token_path=config['token_path'],
                                scopes=config['scopes'])
# APIで送付したいデータ
post_data = {"Date": str(datetime.now()), 
             "Temperature": str(temp),
             "Humidity": str(hum),
             "Pressure": str(pres)}
# API実行
google_script.run_google_script(script_id=config['script_id'], function_name='doPost',
                                parameters=[post_data])