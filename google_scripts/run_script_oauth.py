import pickle
import os.path
from datetime import datetime
import yaml
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class RunScriptOAuth():
    API_SERVICE_NAME = "script"
    API_VERSION = "v1"

    def __init__(self, client_secrets_path, token_path, scopes):
        """
        GASスクリプトをOAuth認証+execution_apiで実行するクラス

        Parameters
        ----------
        client_secrets_path : str
            クライエントシークレットのパス（GCPのOAuthクライアントIDの「client_secrets.json」）
        token_path : str
            トークンを記載したpickleファイルの保存先
        scopes : list
            Google APIのスコープ（リスト指定、スプレッドシートなら`["https://www.googleapis.com/auth/spreadsheets"]`）
        """
        self.service = self._get_authenticated_service(client_secrets_path, token_path, scopes)

    def _get_authenticated_service(self, client_secrets, token_path, scopes):
        creds = None
        if os.path.exists(token_path):  # 認証トークン情報存在時、Pickleから取得
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:  # 認証トークン情報非存在時、認証実行
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets, 
                    scopes=scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:  # 認証トークン情報をPickleに保存
                pickle.dump(creds, token)

        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)

    def run_google_script(self, script_id, function_name, parameters):
        """
        GASスクリプトをOAuth認証+execution_apiで実行

        Parameters
        ----------
        script_id : str
            GASのスクリプトID（GASコンソールの「実行可能APIとして導入」で発行）
        function_name : str
            実行したいGASの関数名
        parameters : list
            GASの関数に渡したい引数（リストの要素順に第1引数, 第2引数‥と代入される）
        """
        # APIに渡すリクエスト
        request = {"function": function_name,  # 実行したい関数名
                   "parameters": parameters}  # 関数に渡す引数
        # スクリプト実行
        response = self.service.scripts().run(body=request, scriptId=script_id).execute()
        print(response)

if __name__ == "__main__":
    with open('./google_scripts/google_creds/google_creds.yaml', encoding='utf-8_sig') as f:
        config=yaml.safe_load(f)
    # スクリプト実行用クラスのインスタンス生成
    google_script = RunScriptOAuth(client_secrets_path=config['client_secrets_path'],
                                   token_path=config['token_path'],
                                   scopes=config['scopes'])
    # APIで送付したいデータ
    post_data = {"Date": str(datetime.now()), 
                 "Temperature": 20,
                 "Humidity": 40}
    # API実行
    google_script.run_google_script(script_id=config['script_id'], function_name='doPost',
                                    parameters=[post_data])