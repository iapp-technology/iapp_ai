# -*- coding: utf-8 -*-
#Example

import iapp_ai
api = iapp_ai.api("iapp-website")
#Normal usage

#api.idcard_front("media/id-card-front.jpg")

#api.idcard_back("media/id-card-back.jpg")

#api.book_bank_api("media/E7393203-15.jpg")

taskGuid = api.face_liveness("media/passport.jpg")
api.info_face_liveness(taskGuid=str(taskGuid))

api.signature_detect("media/signature.jpg")

api.power_meter(headers={'Content-Type': 'application/json'}, image="media/base64.txt")

api.water_meter_binary("media/wm.jpg")
api.water_meter_base64(image="media/water-meter.txt")

# api.thai_qa_api(question="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่", document="จังหวัดแค็วม์โปแลนด์คือหน่วยการปกครองท้องถิ่นของประเทศโปแลนด์ในช่วงปี ค.ศ.1975 - ค.ศ.1998 จังหวัดได้รับการรวมเข้ากับจังหวัดลูบลินมีเมืองหลักคือแค็วม์ใน ปี ค.ศ.1998 มีพื้นที่ประมาณ 3865 ตารางกิโลเมตรและมีประชากร 248800 คน")
api.thai_qgen_api(text="ผมพูดภาษาไทย")

api.thai_asr_api("media/data.wav")
api.thai_thaitts_kaitom("Hello")
api.thai_thaitts_cee("Hello")

api.img_bg_removal("media/base64.txt")

api.face_verification("media/id-card-front.jpg", "media/id-card-front.jpg", "iApp", "0.1")
api.face_ver2("media/id-card-front.jpg", "media/id-card-front.jpg")

api.face_detect_single("media/passport.jpg", "iApp")
api.face_detect_multi("media/passport.jpg", "iApp")
api.face_detect_config_score("0.5","iApp", "1234")

api.face_recog_single("media/id-card-front.jpg", "iApp")
api.face_recog_multi("media/id-card-front.jpg", "iApp")
api.face_recog_facecrop("media/id-card-front.jpg", "iApp")
api.face_recog_add("media/id-card-front.jpg", "iApp", "Panuphong", "1234")
api.face_recog_import("media/file.csv", "iApp", "1234")
api.face_recog_check("iApp", "1234")
api.face_recog_export("iApp", "1234")
api.face_recog_remove("iApp", "Panupong", "1234", "18-05-2022", "01")
api.face_recog_config_score("0.9", "0.5","iApp", "1234")

#Change apikey to the invalid one.
# print(api.idcard_front("media/id-card-front.jpg", headers={"apikey":"123"}))