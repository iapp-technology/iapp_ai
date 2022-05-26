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
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/front", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        return response

    def idcard_back(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/thai-national-id-card/v3/back", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        return response
    
    def license_plate_lpr(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/license-plate-recognition/file", headers=request_headers, data=request_data_payload, files=request_files)
        print(response.text)
        return response 

    def book_bank_api(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/book-bank-ocr/file", headers=request_headers, data=request_data_payload, files=request_files)
        return response 

    def face_liveness(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/passive-face-liveness-detection", headers=request_headers, data=request_data_payload, files=request_files)
        return response

    def info_face_liveness(self, headers={}, taskGuid={}):
        request_headers = {"apikey":self.apikey, **headers}
        
        request_url = "https://api.iapp.co.th/passive-face-liveness-detection/" + taskGuid
        
        response = requests.request("GET", request_url, headers=request_headers)
        return response
    
    # #TODO: Not yet ready
    # def signature_detect(self, file_path, headers={}, data_payload={}, files=[]):
    #     request_headers = {"apikey":self.apikey, **headers}
    #     request_data_payload = {**data_payload}
    #     request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
    #     request_files.extend(files)
        
    #     response = requests.request("POST", "https://api.iapp.co.th/signature-detection/file", headers=request_headers, data=request_data_payload, files=request_files)
    #     return response

    def power_meter(self, headers={}, image= {}):
        request_headers = {"apikey":self.apikey, **headers}
        request_files = open(image,'r')
        data = request_files.read()
        #close file
        request_files.close()
        request_data_payload = json.dumps({
            'image': data})

        response = requests.request("POST", "https://titipakorn.xyz/ocr/api/predict/ocr_detect/", headers=request_headers, data=request_data_payload)
        return response
    
    # #TODO: Not yet ready
    # def water_meter_binary(self, file_path, headers={}, data_payload={}, files=[]):
    #     request_headers = {"apikey":self.apikey, **headers}
    #     request_data_payload = {**data_payload}
    #     request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
    #     request_files.extend(files)
        
    #     response = requests.request("POST", "https://api.iapp.co.th/meter-number-ocr/file", headers=request_headers, data=request_data_payload, files=request_files)
    #     return response
    
    def water_meter_base64(self, headers={}, image={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_files = open(image,'r')
        data = request_files.read()
        #close file
        request_files.close()
        request_data_payload = json.dumps({
            'image': data})

        response = requests.request("POST", "https://titipakorn.xyz/ocr/api/predict/ocr_detect/", headers=request_headers, data=request_data_payload)
        return response

    def thai_qa_api(self, headers={}, question= {}, document={}):
        request_headers = {"apikey":self.apikey, 'Content-Type': 'application/json', **headers}
        request_data_payload = json.dumps({
            'question': question,
            'document': document})

        response = requests.request("POST", "https://api.iapp.co.th/thai-qa/inference", headers=request_headers, data=request_data_payload)
        return response
    
    def thai_qgen_api(self, text={}, headers={}, data_payload={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}

        url = "http://api.iapp.co.th/qa-generator-th?text=" + str(text) + "&apikey=" + str(self.apikey)
        

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)

        return response
    
    def thai_text_summarization(self, text={}, output_length={}, headers={}, data_payload={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}

        url = "https://api.iapp.co.th/text-summarization?text=" + str(text) + "&output_length=" + str(output_length)

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response
    
    def thai_asr_api(self, file_path, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'audio/mpga'))]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/asr", headers=request_headers, data=request_data_payload, files=request_files)
        return response

    def thai_thaitts_kaitom(self, text={}, headers={}, data_payload={} ):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_url = "https://api.iapp.co.th/thai-tts-kaitom/tts?text=" + text

        response = requests.request("GET", request_url, headers=request_headers, data=request_data_payload)
        return response.text

    def thai_thaitts_cee(self, text={}, headers={}, data_payload={} ):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_url = "https://api.iapp.co.th/thai-tts-cee/tts?text=" + text

        response = requests.request("GET", request_url, headers=request_headers, data=request_data_payload)
        return response.text

    def face_verification(self, file_path1, file_path2, company_name, min_score, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name,'min_score': min_score, **data_payload}
        request_files = [('file1',(file_path1, open(file_path1,'rb'),'application/octet-stream')),('file2',(file_path2, open(file_path2,'rb'),'application/octet-stream')) ]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/face_compare", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_ver_config_score(self, detect_value, compare_value, company_name, company_password, headers={}, data_payload={}):

        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'detect_value': detect_value, 'compare_value': compare_value, 'company': company_name, 'password': company_password, **data_payload}
        
        # Config Score
        "https://api.iapp.co.th/face_config_score?detection="+ detect_value+"&comparison="+compare_value+"&company="+company_name+"&password="+company_password

        # Show Score
        url = "https://api.iapp.co.th/face_config_score?detection&comparison&company="+company_name+"&password="+company_password


        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response


    def face_ver2(self, file_path1, file_path2, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {**data_payload}
        request_files = [('file1',(file_path1, open(file_path1,'rb'),'application/octet-stream')),('file2',(file_path2, open(file_path2,'rb'),'application/octet-stream')) ]
        request_files.extend(files)
        
        response = requests.request("POST", "https://api.iapp.co.th/face-verification/v2/face_compare", headers=request_headers, data=request_data_payload, files=request_files)
        return response
        
    def face_detect_single(self,  file_path, company_name, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_detect_single", headers=request_headers, data=request_data_payload, files=request_files)
        return response

    def face_detect_multi(self,  file_path, company_name, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_detect_multi", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_detect_config_score(self, detect_value, company_name, company_password, headers={}, data_payload={}):

        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'detect_value': detect_value, 'company': company_name, 'password': company_password, **data_payload}
        
        # Configure Score
        url = "https://api.iapp.co.th/face_config_score?detection="+detect_value+"&company="+company_name+"&password="+company_password
        
        # Show Score
        url = "https://api.iapp.co.th/face_config_score?detection&company="+company_name+"&password="+company_password

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response

    
    def face_recog_single(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_recog_single", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_recog_multi(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_recog_multi", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_recog_facecrop(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_recog_facecrop", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_recog_add(self, file_path, company_name, name, password, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, 'name': name, 'password': password, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_recog_add", headers=request_headers, data=request_data_payload, files=request_files)
        return response

    def face_recog_import(self, file_path, company_name, password, headers={}, data_payload={}, files=[]):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, 'password': password, **data_payload}
        request_files = [('file',(file_path, open(file_path,'rb'),'text/csv'))]
        request_files.extend(files)
   
        response = requests.request("POST", "https://api.iapp.co.th/face_recog_import", headers=request_headers, data=request_data_payload, files=request_files)
        return response
    
    def face_recog_check(self, company_name, company_password, headers={}, data_payload={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, 'password': company_password, **data_payload}
        
        # None Save File
        url = "https://api.iapp.co.th/face_recog_check?company="+ company_name+ "&password="+ company_password 

        # Save File
        url = "https://api.iapp.co.th/face_recog_check?company="+ company_name+ "&password="+ company_password +"&save_file"

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response
    
    def face_recog_export(self, company_name, company_password, headers={}, data_payload={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, 'password': company_password, **data_payload}
        
        # Save CSV File
        url = "https://api.iapp.co.th/face_recog_export?company="+company_name+"&type_file=csv&password="+company_password

        # Save Excel File
        url = "https://api.iapp.co.th/face_recog_export?company="+company_name+"&type_file=excel&password="+company_password

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response
    
    
    def face_recog_remove(self, company_name, name, company_password, date, face_id, headers={}, data_payload={}):
        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'company': company_name, 'name': name, 'password': company_password,'date': date, 'face_id': face_id, **data_payload}
        
        url = "https://api.iapp.co.th/face_recog_remove?company="+company_name+"&name="+name+"&password="+company_password

        # Remove All Face of This Person Name in This Date
        url = "https://api.iapp.co.th/face_recog_remove?company="+company_name+"&name="+name+"&password="+company_password+"&face_id="+date

        # Remove Only Face of This Person Name By and This Face ID
        url = "https://api.iapp.co.th/face_recog_remove?company="+company_name+"&name="+name+"&password="+company_password+"&face_id="+ face_id

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response

    def face_recog_config_score(self, detect_value, recog_value, company_name, company_password, headers={}, data_payload={}):

        request_headers = {"apikey":self.apikey, **headers}
        request_data_payload = {'detect_value': detect_value,'recog_value':recog_value, 'company': company_name, 'password': company_password, **data_payload}
        
        # Configure Score
        url = "https://api.iapp.co.th/face_config_score?detection="+detect_value+"&recognition="+recog_value+"&company="+company_name+"&password="+company_password
        
        # Show Score
        url = "https://api.iapp.co.th/face_config_score?detection&recognition&company="+company_name+"&password="+company_password

        response = requests.request("GET", url, headers=request_headers, data=request_data_payload)
        return response

    def img_bg_removal(self, file_path, headers={}):
        request_headers = {"apikey":self.apikey,'Content-Type': 'application/json', **headers}
        # request_data_payload = {**data_payload}
        
        text_file = open(file_path, "r")
 
        #read whole file to a string
        data = text_file.read()
        
        #close file
        text_file.close()

        request_data_payload  = json.dumps({
                "rotateIfPortiat": True,
                "content": data 
        })
     

        response = requests.request("POST", "https://api.iapp.co.th/face-extractor/predict" , headers=request_headers, data=request_data_payload)
        return response