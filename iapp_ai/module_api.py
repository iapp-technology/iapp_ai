import requests

class api():
    apikey = ""
    def __init__(self, apikey):
        self.apikey = apikey
    
    def idcard_front(self, file_path):
        files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/front", headers={"apikey":self.apikey},files=files)
        print(response.json())
        return response.json()  #Return as the Object

