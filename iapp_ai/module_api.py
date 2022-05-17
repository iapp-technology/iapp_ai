import requests

class api():
    apikey = ""
    def __init__(self, apikey):
        self.apikey = apikey
    
    def idcard_front(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)

        # print(request_headers)
        # print(request_data_payload)
        # print(request_files)
        
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/front", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.json())
        return response.json()  #Return as the Object

