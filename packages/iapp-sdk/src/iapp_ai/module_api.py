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

import base64
import json
import os
from typing import Any, Dict, List, Optional

import requests

from iapp_core import (
    API_BASE,
    build_output_path,
    build_url,
    open_input_files,
    request_sync,
)


taskGuid = ""


class api():
    apikey = ""
    def __init__(self, apikey):
        self.apikey = apikey


    ################## Thai Natural Language Processing ##################

    def thai_qa_api(self, headers: Optional[Dict[str, Any]] = None, question: Any = "", document: Any = "") -> requests.Response:
        headers = headers or {}
        request_data_payload = json.dumps({
            'question': question,
            'document': document})

        return request_sync("POST", f"{API_BASE}/v3/store/nlp/question/answer/v3",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)

    def thai_qgen_api(self, text: str = "", headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Generate question-answer pairs from a Thai text passage.

        Endpoint: ``GET /v3/store/nlp/question/generation`` with the source text
        sent as the ``text`` query parameter.
        """
        headers = headers or {}
        data_payload = data_payload or {}
        url = build_url(API_BASE, "v3/store/nlp/question/generation", {"text": str(text)})

        return request_sync("GET", url, apikey=self.apikey, headers=headers,
                            data={**data_payload})

    def thai_text_summarization(self, text: str = "", style: Optional[str] = None, language: Optional[str] = None, max_output_tokens: Optional[int] = None, headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Summarize a Thai or English text passage.

        Endpoint: ``POST /v3/store/nlp/thai-text-summary`` with a JSON body.

        Args:
            text: The text to summarize (required).
            style: Summary style — ``standard``, ``clarify`` or ``friendly``.
            language: Output language — ``th`` or ``en``.
            max_output_tokens: Optional cap on the length of the summary.
            headers: Additional HTTP headers to send with the request.
            data_payload: Extra JSON fields merged into the request body.
        """
        headers = headers or {}
        data_payload = data_payload or {}
        body: Dict[str, Any] = {"text": str(text)}
        if style is not None:
            body["style"] = style
        if language is not None:
            body["language"] = language
        if max_output_tokens is not None:
            body["max_output_tokens"] = max_output_tokens
        body.update(data_payload)

        return request_sync("POST", f"{API_BASE}/v3/store/nlp/thai-text-summary",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            json_body=body)

    def eng_thai_translate(self, text: str = "", source_lang: str = "en", target_lang: str = "th", max_length: Optional[int] = None, headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Translate text between supported languages (Thai-optimized).

        Endpoint: ``POST /v3/store/nlp/multilingual-translation`` with a JSON body.

        Args:
            text: The text to translate (required).
            source_lang: Source language code (defaults to ``en``).
            target_lang: Target language code (defaults to ``th``).
            max_length: Optional cap on the number of output tokens.
            headers: Additional HTTP headers to send with the request.
            data_payload: Extra JSON fields merged into the request body.
        """
        headers = headers or {}
        data_payload = data_payload or {}
        body: Dict[str, Any] = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        if max_length is not None:
            body["max_length"] = max_length
        body.update(data_payload)

        return request_sync("POST", f"{API_BASE}/v3/store/nlp/multilingual-translation",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            json_body=body)




    ################## Image Recognition ##################

    def idcard_front(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)
            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/thai-national-id-card/front",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def idcard_front_photocopied(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)
            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/thai-national-id-card-with-signature",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def idcard_back(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/thai-national-id-card/back",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def license_plate_ocr(self, file_path: str, headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None, files: Optional[List[Any]] = None) -> requests.Response:
        headers = headers or {}
        data_payload = data_payload or {}
        files = files or []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as (file_obj,):
            request_files = [('file',(filename, file_obj, 'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/smart-city/license-plate-ocr",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def license_plate_base64(self, headers: Optional[Dict[str, Any]] = None, data_payload: Any = None) -> requests.Response:
        headers = headers or {}
        request_data_payload = json.dumps({
            'image': data_payload})

        return request_sync("POST", f"{API_BASE}/v3/store/smart-city/license-plate-ocr/base64",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)


    def book_bank_api(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/book-bank",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def passport_ocr(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/passport",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_plaintext(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/document/ocr",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_json_layout(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/document/layout",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def document_ocr_docx(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh))]
            request_files.extend(files)

            response = request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/document/docx",
                                    apikey=self.apikey, headers=headers,
                                    data={**data_payload}, files=request_files)
            return response


    def face_liveness(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Check whether a face photo is of a real live person or a spoof.

        Args:
            file_path: Path to the face image file.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        global taskGuid
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            response = request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-passive-liveness",
                                    apikey=self.apikey, headers=headers,
                                    data={**data_payload}, files=request_files)
            try:
                taskGuid = response.json().get("taskGuid", "")
            except Exception:
                taskGuid = ""

            return response

    def info_face_liveness(
        self,
        headers: Optional[Dict[str, str]] = None,
        taskGuid: str = "",
        url: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Retrieve results for an asynchronous face liveness check.

        Args:
            headers: Additional HTTP headers to send with the request.
            taskGuid: Task ID of the liveness check to query.
            url: Unused legacy parameter preserved for backward compatibility.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if url is None:
            url = []
        request_url = "https://api.iapp.co.th/v3/store/ekyc/face-passive-liveness/" + taskGuid
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

    def power_meter(self, headers: Optional[Dict[str, Any]] = None, image: str = "") -> requests.Response:
        """Read the number from a power/water meter image (base64 variant).

        Endpoint: ``POST /v3/store/smart-city/power-meter-and-water-meter``
        with the image base64-encoded in a JSON body ``{"image": ...}``.
        """
        headers = headers or {}
        with open_input_files([image]) as (image_file,):
            data = base64.b64encode(image_file.read()).decode("ascii")
        request_data_payload = json.dumps({
            'image': data})

        return request_sync("POST", f"{API_BASE}/v3/store/smart-city/power-meter-and-water-meter",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)


    def water_meter_binary(self, file_path: str, headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None, files: Optional[List[Any]] = None) -> requests.Response:
        headers = headers or {}
        data_payload = data_payload or {}
        files = files or []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as (file_obj,):
            request_files = [('file', (filename, file_obj, 'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/smart-city/power-meter-and-water-meter/file",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def water_meter_base64(self, headers: Optional[Dict[str, Any]] = None, data_payload: Any = None) -> requests.Response:
        headers = headers or {}
        request_data_payload = json.dumps({
            'image': data_payload})

        return request_sync("POST", f"{API_BASE}/v3/store/smart-city/power-meter-and-water-meter/base64",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=request_data_payload)

    def face_verification(
        self,
        file_path1: str,
        file_path2: str,
        company_name: str,
        min_score: float,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Compare two face images (1:1 verification).

        Args:
            file_path1: Path to the first face image.
            file_path2: Path to the second face image.
            company_name: Company name / namespace.
            min_score: Threshold match score (0-100).
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename1 = os.path.basename(file_path1)
        filename2 = os.path.basename(file_path2)
        request_data_payload = {'company': company_name, 'threshold': min_score, **data_payload}
        with open_input_files([file_path1, file_path2]) as [fh1, fh2]:
            request_files = [('file1',(filename1, fh1,'application/octet-stream')),('file2',(filename2, fh2,'application/octet-stream')) ]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-verification",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_id_card_verification(
        self,
        id_card_path: str,
        selfie_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Verify that a selfie matches the face photo on a Thai national ID card.

        The core eKYC identity check: compares a selfie against the face on an ID
        card and returns per-image and total confidence plus ``isSamePerson``
        verdicts. Unlike :meth:`face_verification` (face-to-face 1:1), this pairs a
        selfie with the photo extracted from the ID card.

        Args:
            id_card_path: Path to the ID card image (JPG/PNG, min 600x400, max 10MB).
            selfie_path: Path to the selfie image (same constraints).
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename0 = os.path.basename(id_card_path)
        filename1 = os.path.basename(selfie_path)
        with open_input_files([id_card_path, selfie_path]) as [fh0, fh1]:
            request_files = [('file0',(filename0, fh0,'application/octet-stream')),('file1',(filename1, fh1,'application/octet-stream'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-and-id-card-verification",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def _face_config_score(self, data_payload, headers=None):
        if headers is None:
            headers = {}
        return request_sync("POST", "https://api.iapp.co.th/face_config_score",
                            apikey=self.apikey, headers=headers,
                            data=data_payload)

    def face_ver_config_score(
        self,
        detect_value: float,
        compare_value: float,
        company_name: str,
        company_password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Configure face verification matching scores for a company.

        Args:
            detect_value: Detection threshold value.
            compare_value: Verification threshold value.
            company_name: Company name / namespace.
            company_password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to configure.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'detect_value': detect_value, 'compare_value': compare_value, 'company': company_name, 'password': company_password, **data_payload}
        return self._face_config_score(request_data_payload, headers=headers)


    def face_ver2(
        self,
        file_path1: str,
        file_path2: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Compare two face images using the V2 face verification API.

        Args:
            file_path1: Path to the first face image.
            file_path2: Path to the second face image.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename1 = os.path.basename(file_path1)
        filename2 = os.path.basename(file_path2)
        with open_input_files([file_path1, file_path2]) as [fh1, fh2]:
            request_files = [('file1',(filename1, fh1,'image/jpg')),('file2',(filename2, fh2,'image/jpg')) ]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-verification",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def face_detect_single(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Detect a single face in an image.

        Args:
            file_path: Path to the image file.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-detection/single",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def face_detect_multi(
        self,
        file_path: str,
        company_name: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Detect multiple faces in an image.

        Args:
            file_path: Path to the image file.
            company_name: Company name / namespace.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-detection/multi",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_detect_config_score(
        self,
        detect_value: float,
        company_name: str,
        company_password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Configure face detection scores for a company.

        Args:
            detect_value: Detection threshold score value.
            company_name: Company name / namespace.
            company_password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to configure.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'detect_value': detect_value, 'company': company_name, 'password': company_password, **data_payload}
        return self._face_config_score(request_data_payload, headers=headers)


    def face_recog_single(
        self,
        file_path: str,
        company_name: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Recognize a single face from a company database (1:N recognition).

        Args:
            file_path: Path to the image file containing the face.
            company_name: Company namespace to search.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-recognition/single",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_recog_multi(
        self,
        file_path: str,
        company_name: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Recognize multiple faces from a company database.

        Args:
            file_path: Path to the image file containing faces.
            company_name: Company namespace to search.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-recognition/multi",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_recog_facecrop(
        self,
        file_path: str,
        company_name: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Crop and recognize a face from a company database.

        Args:
            file_path: Path to the image file containing the face.
            company_name: Company namespace to search.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-recognition/facecrop",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_recog_add(
        self,
        file_path: str,
        company_name: str,
        name: str,
        password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Enroll/add a face to a company database.

        Args:
            file_path: Path to the face image file.
            company_name: Company namespace.
            name: Name of the person to associate with the face.
            password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, 'name': name, 'password': password, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpeg'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-recognition/add",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_recog_import(
        self,
        file_path: str,
        company_name: str,
        password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
    ) -> requests.Response:
        """Import multiple faces from a CSV file.

        Args:
            file_path: Path to the CSV file.
            company_name: Company namespace.
            password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {'company': company_name, 'password': password, **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'text/csv'))]
            request_files.extend(files)

            return request_sync("POST", "https://api.iapp.co.th/v3/store/ekyc/face-recognition/import",
                                apikey=self.apikey, headers=headers,
                                data=request_data_payload, files=request_files)

    def face_recog_check(
        self,
        company_name: str,
        company_password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Check all faces in a company namespace database.

        Args:
            company_name: Company namespace.
            company_password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to send.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'company': company_name, 'password': company_password, **data_payload}

        url = "https://api.iapp.co.th/v3/store/ekyc/face-recognition/check"
        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_export(
        self,
        company_name: str,
        company_password: str,
        type_file: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Export face database records for a company namespace.

        Args:
            company_name: Company namespace.
            company_password: Password for authentication.
            type_file: Format of the exported file.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to send.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'company': company_name, 'password': company_password, 'type_file': type_file, **data_payload}

        url = "https://api.iapp.co.th/v3/store/ekyc/face-recognition/export"

        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_remove(
        self,
        company_name: str,
        name: str,
        company_password: str,
        date: str,
        face_id: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Remove a face record from a company database.

        Args:
            company_name: Company namespace.
            name: Name of the person.
            company_password: Password for authentication.
            date: Registration date.
            face_id: ID of the face to remove.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to send.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'company': company_name, 'name': name, 'password': company_password,'date': date, 'face_id': face_id, **data_payload}

        url = "https://api.iapp.co.th/v3/store/ekyc/face-recognition/remove"
        return request_sync("POST", url, apikey=self.apikey, headers=headers,
                            data=request_data_payload)

    def face_recog_config_score(
        self,
        detect_value: float,
        recog_value: float,
        company_name: str,
        company_password: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Configure face recognition scores for a company namespace.

        Args:
            detect_value: Detection threshold value.
            recog_value: Recognition threshold value.
            company_name: Company namespace.
            company_password: Password for authentication.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional parameters to configure.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        request_data_payload = {'detect_value': detect_value,'recog_value':recog_value, 'company': company_name, 'password': company_password, **data_payload}
        return self._face_config_score(request_data_payload, headers=headers)

    def img_bg_removal_base64(
        self,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Any] = None,
    ) -> requests.Response:
        """Remove background from an image supplied as a base64 string.

        Args:
            headers: Additional HTTP headers to send with the request.
            data_payload: Base64 string payload of the image.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        import base64
        import io
        if headers is None:
            headers = {}
        if data_payload is None:
            img_bytes = b""
        else:
            try:
                img_bytes = base64.b64decode(data_payload)
            except Exception:
                img_bytes = b""
        request_files = [('file', ('image.jpg', io.BytesIO(img_bytes), 'image/jpeg'))]
        request_data_payload = {
             "rotateIfPortiat": True
        }
        return request_sync("POST", "https://api.iapp.co.th/v3/store/smart-city/remove-background",
                            apikey=self.apikey, headers=headers,
                            data=request_data_payload, files=request_files)

    def img_bg_removal_file(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
        output_path: Optional[str] = None,
    ) -> requests.Response:
        """Remove background from an image file and save the result.

        Args:
            file_path: Path to the image file.
            headers: Additional HTTP headers to send with the request.
            data_payload: Additional form-data parameters to send.
            files: Additional files to upload.
            output_path: Optional path to save the output file.

        Returns:
            requests.Response: The HTTP response from the API server.
        """
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        request_data_payload = {
             "rotateIfPortiat": True,
             **data_payload}
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            response = request_sync("POST", "https://api.iapp.co.th/v3/store/smart-city/remove-background",
                                    apikey=self.apikey, headers=headers,
                                    data=request_data_payload, files=request_files)
            target_path = build_output_path("img_bg_removal_file.jpg", output_path)
            with open(target_path, "wb") as file:
                file.write(response.content)
            return response

    def driver_card_ocr(
        self,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Any]] = None,
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
        if headers is None:
            headers = {}
        if data_payload is None:
            data_payload = {}
        if files is None:
            files = []
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            request_files = [('file',(filename, fh,'image/jpg'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/ekyc/thai-driver-license",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)


    ################## Voice and Speech ##################

    def thai_asr_api(self, file_path: str, headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None, files: Optional[List[Any]] = None) -> requests.Response:
        """Transcribe a Thai audio file to text.

        Endpoint: ``POST /v3/store/speech/speech-to-text/base``, sent as
        multipart form-data with the audio under the ``file`` field. Optional
        form fields (e.g. ``chunk_size``, ``use_asr_pro``) may be supplied via
        ``data_payload``.
        """
        headers = headers or {}
        data_payload = data_payload or {}
        files = files or []
        with open_input_files([file_path]) as (file_obj,):
            request_files = [('file',(file_path, file_obj, 'audio/mpga'))]
            request_files.extend(files)

            return request_sync("POST", f"{API_BASE}/v3/store/speech/speech-to-text/base",
                                apikey=self.apikey, headers=headers,
                                data={**data_payload}, files=request_files)

    def thai_thaitts_kaitom(self, text: str = "", headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> requests.Response:
        """Synthesize Thai speech and save the audio to a local file.

        Endpoint: ``POST /v3/store/audio/tts`` with a JSON body ``{"text": ...}``.
        The response audio is written to ``output_path`` (defaults to
        ``kaitom.wav`` in the output directory).
        """
        headers = headers or {}
        data_payload = data_payload or {}
        body = {"text": text, **data_payload}

        response = request_sync("POST", f"{API_BASE}/v3/store/audio/tts",
                                apikey=self.apikey,
                                headers={'Content-Type': 'application/json', **headers},
                                json_body=body)
        path = build_output_path("kaitom.wav", output_path)
        with open(path, "wb") as file:
            file.write(response.content)
        return response

    def thai_thaitts_cee(self, text: str = "", headers: Optional[Dict[str, Any]] = None, data_payload: Optional[Dict[str, Any]] = None, output_path: Optional[str] = None) -> requests.Response:
        """Synthesize Thai speech and save the audio to a local file.

        Endpoint: ``GET /v3/store/speech/text-to-speech/cee`` with query params ``text``.
        The response audio is written to ``output_path`` (defaults to
        ``cee.wav`` in the output directory).
        """
        headers = headers or {}
        data_payload = data_payload or {}
        params = {"text": text, **data_payload}

        response = request_sync("GET", f"{API_BASE}/v3/store/speech/text-to-speech/cee",
                                apikey=self.apikey,
                                headers=headers,
                                params=params)
        path = build_output_path("cee.wav", output_path)
        with open(path, "wb") as file:
            file.write(response.content)
        return response

    ############## APIs added to match api docs (iapp.co.th/docs) ##############
    # Endpoints mirror the verified iapp-mcp tools. Every method returns the raw
    # requests.Response, consistent with the rest of this SDK.

    def llm_chat(
        self,
        prompt: str = "",
        model: str = "chinda-qwen3-4b",
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Chat with iApp-hosted LLMs (OpenAI-compatible).

        model: chinda-qwen3-4b | deepseek-reasoner | deepseek-chat |
        deepseek-v4-flash | deepseek-v4-pro.
        """
        headers = headers or {}
        endpoints = {
            "chinda-qwen3-4b": "https://api.iapp.co.th/v3/llm/chinda-thaillm-4b/chat/completions",
            "deepseek-reasoner": "https://api.iapp.co.th/v3/llm/deepseek-3p2/chat/completions",
            "deepseek-chat": "https://api.iapp.co.th/v3/llm/deepseek-3p2/chat/completions",
            "deepseek-v4-flash": "https://api.iapp.co.th/v3/llm/deepseek-v4/chat/completions",
            "deepseek-v4-pro": "https://api.iapp.co.th/v3/llm/deepseek-v4/chat/completions",
        }
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        })
        return request_sync("POST", endpoints[model], apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=payload)

    def thanoy_legal_qa(self, query: str = "", headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thanoy Thai Legal AI chatbot (ทนายAI)."""
        headers = headers or {}
        payload = json.dumps({"query": query})
        return request_sync("POST", f"{API_BASE}/v3/store/llm/thanoy-legal-ai", apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=payload)

    def image_generation(self, prompt: str = "", model: str = "nanobanana", headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Generate an image (Google Nano Banana). model: nanobanana | nanobanana-pro."""
        headers = headers or {}
        slug = "nanobanana" if model == "nanobanana" else "nanobananapro"
        url = f"https://api.iapp.co.th/v3/image/generation/google/{slug}/generate"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        })
        return request_sync("POST", url, apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=payload)

    def seedance_video_submit(
        self,
        prompt: str = "",
        model: str = "seedance-fast",
        duration: int = 5,
        ratio: str = "16:9",
        resolution: str = "720p",
        generate_audio: bool = True,
        watermark: bool = False,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Submit an async Seedance 2.0 video job. Poll with seedance_video_status()."""
        headers = headers or {}
        model_ids = {
            "seedance": "dreamina-seedance-2-0-260128",
            "seedance-fast": "dreamina-seedance-2-0-fast-260128",
        }
        payload = json.dumps({
            "model": model_ids[model],
            "content": [{"type": "text", "text": prompt}],
            "duration": duration,
            "ratio": ratio,
            "resolution": resolution,
            "generate_audio": generate_audio,
            "watermark": watermark,
        })
        return request_sync("POST", "https://api.iapp.co.th/v3/store/video/seedance/tasks",
                            apikey=self.apikey,
                            headers={'Content-Type': 'application/json', **headers},
                            data=payload)

    def seedance_video_status(self, task_id: str = "", headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Check a Seedance video job status; returns the download URL when done."""
        headers = headers or {}
        url = "https://api.iapp.co.th/v3/store/video/seedance/tasks/" + str(task_id)
        return request_sync("GET", url, apikey=self.apikey, headers=headers)

    def receipt_ocr(self, file_path: str, return_ocr: bool = False, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai receipt / tax-invoice OCR."""
        headers = headers or {}
        data = {"return_ocr": "true"} if return_ocr else {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/receipt",
                                apikey=self.apikey, headers=headers,
                                data=data, files=[('file', (filename, fh))])

    def credit_card_statement_ocr(self, file_path: str, return_ocr: bool = False, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai credit card statement OCR."""
        headers = headers or {}
        data = {"return_ocr": "true"} if return_ocr else {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/creditcard-statement",
                                apikey=self.apikey, headers=headers,
                                data=data, files=[('file', (filename, fh))])

    def tax_deduction_certificate_ocr(self, file_path: str, return_ocr: bool = False, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai withholding tax deduction certificate (50 ทวิ) OCR."""
        headers = headers or {}
        data = {"return_ocr": "true"} if return_ocr else {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/tax-deduction-certificate",
                                apikey=self.apikey, headers=headers,
                                data=data, files=[('file', (filename, fh))])

    def civil_registration_ocr(self, file_path: str, return_ocr: bool = False, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai civil registration certificate OCR."""
        headers = headers or {}
        data = {"return_ocr": "true"} if return_ocr else {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/civil-registeration-certificate",
                                apikey=self.apikey, headers=headers,
                                data=data, files=[('file', (filename, fh))])

    def resume_ocr(self, file_path: str, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """AI resume / CV extraction and evaluation."""
        headers = headers or {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/curriculum-vitae",
                                apikey=self.apikey, headers=headers,
                                files=[('file', (filename, fh))])

    def job_description_ocr(self, file_path: str, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """AI job description extraction."""
        headers = headers or {}
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/ocr/job-description",
                                apikey=self.apikey, headers=headers,
                                files=[('file', (filename, fh))])

    def speech_to_text(
        self,
        file_path: str,
        language: str = "th",
        quality: str = "base",
        chunk_size: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Speech-to-text with diarization. language: th|en|zh, quality: base|pro."""
        headers = headers or {}
        paths = {
            ("th", "base"): "/v3/store/speech/speech-to-text/base",
            ("th", "pro"): "/v3/store/speech/speech-to-text/pro",
            ("en", "base"): "/v3/store/speech/speech-to-text/base/en",
            ("en", "pro"): "/v3/store/speech/speech-to-text/pro/en",
            ("zh", "base"): "/v3/store/speech/speech-to-text/base/zh",
            ("zh", "pro"): "/v3/store/speech/speech-to-text/pro/zh",
        }
        url = "https://api.iapp.co.th" + paths[(language, quality)]
        data: Dict[str, Any] = {}
        if chunk_size is not None:
            data["chunk_size"] = str(chunk_size)
        filename = os.path.basename(file_path)
        with open_input_files([file_path]) as [fh]:
            return request_sync("POST", url, apikey=self.apikey, headers=headers,
                                data=data, files=[('file', (filename, fh))])

    def voice_clone_tts(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        speed: float = 1.0,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Voice cloning TTS from a short reference audio sample."""
        headers = headers or {}
        data = {"text": text, "ref_text": ref_text, "speed": str(speed)}
        filename = os.path.basename(ref_audio_path)
        with open_input_files([ref_audio_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/audio/tts/clone",
                                apikey=self.apikey, headers=headers,
                                data=data, files=[('ref_audio', (filename, fh))])

    def ai_audio_detection(self, audio_path: str, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Detect whether audio was AI-generated (iApp TTS watermark detection)."""
        headers = headers or {}
        filename = os.path.basename(audio_path)
        with open_input_files([audio_path]) as [fh]:
            return request_sync("POST", "https://api.iapp.co.th/v3/store/audio/tts/detect",
                                apikey=self.apikey, headers=headers,
                                files=[('audio', (filename, fh))])

    def sentiment_analysis(self, text: str = "", headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai sentiment analysis (positive / neutral / negative)."""
        headers = headers or {}
        return request_sync("POST", "https://api.iapp.co.th/v3/store/nlp/sentiment-analysis",
                            apikey=self.apikey, headers=headers, params={"text": text})

    def toxicity_classification(self, text: str = "", headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Thai text toxicity classification."""
        headers = headers or {}
        return request_sync("POST", "https://api.iapp.co.th/v3/store/nlp/toxicity-classification",
                            apikey=self.apikey, headers=headers, params={"text": text})

    def thai_holidays(
        self,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        holiday_type: str = "public",
        days_after: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Thai public holiday data (by year, by date range, or around today)."""
        headers = headers or {}
        params: Dict[str, Any] = {"holiday_type": holiday_type}
        if year is not None:
            url = "https://api.iapp.co.th/v3/store/data/thai-holiday/year/" + str(year)
        elif start_date and end_date:
            url = "https://api.iapp.co.th/v3/store/data/thai-holiday/range"
            params["start_date"] = start_date
            params["end_date"] = end_date
        else:
            url = "https://api.iapp.co.th/v3/store/data/thai-holiday"
            if days_after is not None:
                params["days_after"] = str(days_after)
        return request_sync("GET", url, apikey=self.apikey, headers=headers, params=params)
