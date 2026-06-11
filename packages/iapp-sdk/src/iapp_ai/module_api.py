"""iApp AI Marketplace Python SDK.

The ``api`` class is a thin, synchronous wrapper around the iApp AI Marketplace
REST API. Every method returns the raw ``requests.Response`` (it does **not**
raise on HTTP errors — inspect ``response.status_code`` / ``response.text`` /
``response.json()`` yourself), exactly as in previous releases.

Internally the HTTP call is delegated to ``iapp_core.request_sync`` so transport,
auth and the base configuration are shared with the rest of the iApp tooling.
The endpoints, request shapes and return values are unchanged for backward
compatibility.
"""

import json
import os
from typing import Dict, Any, List

import requests
from iapp_core import request_sync, open_input_files


class api():
    apikey = ""
    def __init__(self, apikey):
        self.apikey = apikey


    ################## Thai Natural Language Processing ##################

    def thai_qa_api(self, headers={}, question= {}, document={}):
        request_data_payload = json.dumps({
            'question': question,
            'document': document})

        return request_sync("POST", "https://api.iapp.co.th/thai-qa/inference",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)

    def thai_qgen_api(self, text={}, headers={}, data_payload={}):
        url = "http://api.iapp.co.th/qa-generator-th?text=" + str(text) + "&apikey=" + str(self.apikey)

        return request_sync("GET", url, apikey=self.apikey, headers=headers,
                            data={**data_payload})

    def thai_text_summarization(self, text={}, output_length={}, headers={}, data_payload={}):
        url = "https://api.iapp.co.th/text-summarization?text=" + str(text) + "&output_length=" + str(output_length)

        return request_sync("GET", url, apikey=self.apikey, headers=headers,
                            data={**data_payload})

    def eng_thai_translate(self, text={}, headers={}, data_payload={}):
        url = "https://api.iapp.co.th/translate/auto?text="+text

        return request_sync("GET", url, apikey=self.apikey, headers=headers,
                            data={**data_payload})

    # #TODO: Will be Fixed
    # def thai_text_parser(self, text={}, headers={}, data_payload={}):
    #     request_headers = {"apikey":self.apikey, 'Content-Type': 'application/json', **headers}
    #     request_data_payload = {**data_payload}

    #     url = "https://api.iapp.co.th/text-thai-parser/parse/"+text

    #     response = requests.request("GET", url, headers=request_headers, data=request_data_payload)

    #     print(json.loads(response.text))
    #     return response



    ################## Image Recognition ##################

    def idcard_front(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract information from the front side of a Thai National ID Card.

        Args:
            file_path: Path to the image file of the front side of the ID card.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)
            return request_sync("POST", "https://api.iapp.co.th/thai-national-id-card/v3/front",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def idcard_front_photocopied(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract information from a photocopied/signed Thai National ID Card front.

        Args:
            file_path: Path to the image file of the photocopied ID card front.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)
            return request_sync("POST", "https://api.iapp.co.th/thai-national-id-card-with-signature/front",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def idcard_back(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract information from the back side of a Thai National ID Card.

        Args:
            file_path: Path to the image file of the back side of the ID card.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/thai-national-id-card/v3.5/back",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def license_plate_ocr(self, file_path, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/license-plate-recognition/file",
                            apikey=self.apikey, headers=headers,
                            data={**data_payload}, files=request_files)

    def license_plate_base64(self, headers={}, data_payload={}):
        request_data_payload = json.dumps({
            'image': data_payload})

        return request_sync("POST", "https://api.iapp.co.th/iapp_license_plate_recognition_v1_base64",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)


    def book_bank_api(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract details from a Thai bank book page (Book Bank).

        Args:
            file_path: Path to the image file of the bank book page.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/book-bank-ocr/file",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def passport_ocr(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract MRZ details from a passport page.

        Args:
            file_path: Path to the image file of the passport.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/passport-ocr/ocr",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_plaintext(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan a general document and extract its plaintext contents.

        Args:
            file_path: Path to the document file (image/PDF).
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/document-ocr/ocr",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_json_layout(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan a general document and extract details including layout positioning in JSON.

        Args:
            file_path: Path to the document file (image/PDF).
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/document-ocr/layout",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_docx(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan a general document and convert/reconstruct it into a downloadable DOCX file.

        Args:
            file_path: Path to the document file (image/PDF).
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response containing the DOCX file link.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            response = request_sync("POST", "https://api.iapp.co.th/document-ocr/docx",
                                    apikey=self.apikey, headers=headers,
                                    data={**data_payload}, files=request_files)
            return response


    def face_liveness(self, file_path, headers={}, data_payload={}, files=[]):
        global taskGuid
        request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)

        response = request_sync("POST", "https://api.iapp.co.th/passive-face-liveness-detection",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)
        taskGuid = response

        return response

    def info_face_liveness(self, headers={}, taskGuid='', url=[]):
        request_url = "https://api.iapp.co.th/passive-face-liveness-detection/" + taskGuid
        # print(request_url)

        return request_sync("GET", request_url, apikey=self.apikey, headers=headers)

    # #TODO: Not yet ready
    # def signature_detect(self, file_path, headers={}, data_payload={}, files=[]):
    #     request_headers = {"apikey":self.apikey, **headers}
    #     request_data_payload = {**data_payload}
    #     request_files = [('file',(file_path, open(file_path,'rb'),'image/jpg'))]
    #     request_files.extend(files)
    #
    #     response = requests.request("POST", "https://api.iapp.co.th/signature-detection/file", headers=request_headers, data=request_data_payload, files=request_files)
    #     return response

    def power_meter(self, headers={}, image= {}):
        request_files = open(image,'r')
        data = request_files.read()
        #close file
        request_files.close()
        request_data_payload = json.dumps({
            'image': data})

        return request_sync("POST", "https://titipakorn.xyz/ocr/api/predict/ocr_detect/",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload)


    def water_meter_binary(self, file_path, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/meter-number-ocr/file",
                            apikey=self.apikey, headers=headers,
                            data={**data_payload}, files=request_files)

    def water_meter_base64(self, headers={}, data_payload={}):
        request_data_payload = json.dumps({
            'image': data_payload})

        return request_sync("POST", "https://api.iapp.co.th/meter-number-ocr/base64",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)

    def face_verification(self, file_path1, file_path2, company_name, min_score, headers={}, data_payload={}, files=[]):
        filename1 = os.path.basename(file_path1)
        filename2 = os.path.basename(file_path2)
        request_data_payload = {'company': company_name,'min_score': min_score, **data_payload}
        request_files = [('file1',(filename1, open(file_path1,'rb'),'application/octet-stream')),('file2',(filename2, open(file_path2,'rb'),'application/octet-stream')) ]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_compare",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_ver_config_score(self, detect_value, compare_value, company_name, company_password, headers={}, data_payload={}):
        request_data_payload = {'detect_value': detect_value, 'compare_value': compare_value, 'company': company_name, 'password': company_password, **data_payload}

        url = "https://api.iapp.co.th/face_config_score"

        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)


    def face_ver2(self, file_path1, file_path2, headers={}, data_payload={}, files=[]):
        filename1 = os.path.basename(file_path1)
        filename2 = os.path.basename(file_path2)
        request_files = [('file1',(filename1, open(file_path1,'rb'),'image/jpg')),('file2',(filename2, open(file_path2,'rb'),'image/jpg')) ]
        request_files.extend(files)

        return request_sync("POST", 'https://api.iapp.co.th/face-verification/v2/face_compare',
                            apikey=self.apikey, headers=headers,
                            data={**data_payload}, files=request_files)

    def face_detect_single(self,  file_path, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_detect_single",
                            apikey=self.apikey, headers=headers,
                            data={**data_payload}, files=request_files)

    def face_detect_multi(self,  file_path, company_name, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_detect_multi",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_detect_config_score(self, detect_value, company_name, company_password, headers={}, data_payload={}):
        request_data_payload = {'detect_value': detect_value, 'company': company_name, 'password': company_password, **data_payload}

        # Configure Score
        url = "https://api.iapp.co.th/face_config_score"

        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)


    def face_recog_single(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_recog_single",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_recog_multi(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_recog_multi",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_recog_facecrop(self, file_path, company_name, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_recog_facecrop",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_recog_add(self, file_path, company_name, name, password, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, 'name': name, 'password': password, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpeg'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_recog_add",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_recog_import(self, file_path, company_name, password, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, 'password': password, **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'text/csv'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/face_recog_import",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def face_recog_check(self, company_name, company_password, headers={}, data_payload={}):
        request_data_payload = {'company': company_name, 'password': company_password, **data_payload}

        url = "https://api.iapp.co.th/face_recog_check"
        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_export(self, company_name, company_password, type_file, headers={}, data_payload={}):
        request_data_payload = {'company': company_name, 'password': company_password, 'type_file': type_file, **data_payload}

        url = "https://api.iapp.co.th/face_recog_export"

        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_remove(self, company_name, name, company_password, date, face_id, headers={}, data_payload={}):
        request_data_payload = {'company': company_name, 'name': name, 'password': company_password,'date': date, 'face_id': face_id, **data_payload}

        url = "https://api.iapp.co.th/face_recog_remove"
        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_config_score(self, detect_value, recog_value, company_name, company_password, headers={}, data_payload={}):
        request_data_payload = {'detect_value': detect_value,'recog_value':recog_value, 'company': company_name, 'password': company_password, **data_payload}

        # Configure Score
        url = "https://api.iapp.co.th/face_config_score"
        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def img_bg_removal_base64(self,headers={}, data_payload={}):
        request_data_payload = json.dumps({
            'content': data_payload,
            "rotateIfPortiat": True
            })
        return request_sync("POST", "https://api.iapp.co.th/face-extractor/predict",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)

    def img_bg_removal_file(self, file_path, headers={}, data_payload={}, files=[]):
        filename = os.path.basename(file_path)
        request_data_payload = {
             "rotateIfPortiat": True,
             **data_payload}
        request_files = [('file',(filename, open(file_path,'rb'),'image/jpg'))]
        request_files.extend(files)

        response = request_sync("POST", "https://api.iapp.co.th/face-extractor/predict/file",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)
        with open("media/img_bg_removal_file.jpg", "wb") as file:
            file.write(response.content)
        return response

    def driver_card_ocr(
        self,
        file_path: str,
        headers: Dict[str, str] = {},
        data_payload: Dict[str, Any] = {},
        files: List[Any] = [],
    ) -> requests.Response:
        """Scan and extract details from a Thai Driver's License Card.

        Args:
            file_path: Path to the image file of the driver's license.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/thai-driver-license-ocr",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)


    ################## Voice and Speech ##################

    def thai_asr_api(self, file_path, headers={}, data_payload={}, files=[]):
        request_files = [('file',(file_path, open(file_path,'rb'),'audio/mpga'))]
        request_files.extend(files)

        return request_sync("POST", "https://api.iapp.co.th/asr",
                            apikey=self.apikey, headers=headers,
                            data={**data_payload}, files=request_files)

    def thai_thaitts_kaitom(self, text={}, headers={}, data_payload={} ):
        request_url = "https://api.iapp.co.th/thai-tts-kaitom/tts?text=" + text

        response = request_sync("GET", request_url, apikey=self.apikey, headers=headers,
                                data={**data_payload})
        with open("media/kaitom.wav", "wb") as file:
            file.write(response.content)
        return response

    def thai_thaitts_cee(self, text={}, headers={}, data_payload={} ):
        request_url = "https://api.iapp.co.th/thai-tts-cee/tts?text=" + text

        response = request_sync("GET", request_url, apikey=self.apikey, headers=headers,
                                data={**data_payload})
        with open("media/cee.wav", "wb") as file:
            file.write(response.content)
        return response
