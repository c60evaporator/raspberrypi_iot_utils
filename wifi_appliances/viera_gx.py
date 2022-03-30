import panasonic_viera

#Vieraから各種情報を取得するクラス
class GetVieraData():
    #人感タグデータ取得
    def get_gx850_data(self, IP):
        #データ取得用クラス作成
        rc = panasonic_viera.RemoteControl(IP)
        #音量取得
        try:
            volume = rc.getVolume()
            rdict = {'Power':1, 'Volume':volume}
        #音量取得できなかったとき、テレビ電源オフとみなす
        except:
            rdict = {'Power':0, 'Volume':None}

        return rdict