import requests

class api():
    apikey = ""
    def __init__(self, apikey):
        self.apikey = apikey
    
    def idcard_front(self, file_path, additional_headers={}, additional_data_payload={}, additional_files=[]):
        headers = {"apikey":self.apikey, **additional_headers}
        data_payload = {**additional_data_payload}
        files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        files.extend(additional_files)

        print(headers)
        print(data_payload)
        print(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/front", headers=headers, data=data_payload, files=files)
        print(response.json())
        return response.json()  #Return as the Object

