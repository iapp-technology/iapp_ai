import requests
import json

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

    def idcard_back(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/back", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.json())
        return response.json()  #Return as the Object

    def book_bank_api(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/book-bank-ocr/file", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        # return response.json()  #Return as the Object

    def face_liveness(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/passive-face-liveness-detection", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.json())

        return response.json()  #Return as the Object
    def info_face_liveness(self, headers={}, taskGuid={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_url = "https://api.iapp.co.th/passive-face-liveness-detection/" + taskGuid

        response = requests.request("GET", request_url, headers=request_headers)
        print(response.json())
        return response.json()  #Return as the Object
    
    def signature_detect(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/book-bank-ocr/file", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        # return response.json() #Return as the Object

    def water_meter_binary(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/meter-number-ocr/file", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        return response.text  #Return as the Object
     

    def thai_qa_api(self, headers={}, question= {}, document={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = json.dumps({
            'question': question,
            'document': document})

        response = requests.request("POST", "https://api.iapp.co.th/thai-qa/inference", headers=request_headers, data=request_data_payload)
        print(response.text)
        return response.text
    
    def thai_asr_api(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'audio/mpga'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/asr", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.json())
        return response.json()  #Return as the Object

    def thai_thaitts_kaitom(self, text={},headers={}, data_payload={} ):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_url = "https://api.iapp.co.th/thai-tts-kaitom/tts?text=" + text

        response = requests.request("GET", request_url, headers=request_headers, data=request_data_payload)
        print(response.text)
        return response.text

    def thai_thaitts_cee(self, text={},headers={}, data_payload={} ):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_url = "https://api.iapp.co.th/thai-tts-cee/tts?text=" + text

        response = requests.request("GET", request_url, headers=request_headers, data=request_data_payload)
        print(response.text)
        return response.text
        
        
