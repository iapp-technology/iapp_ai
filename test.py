# -*- coding: utf-8 -*-
#Example

import iapp_ai
api = iapp_ai.api("iapp-website")
#Normal usage
api.idcard_front("media/id-card-front.jpg")
print("----")
api.idcard_back("media/id-card-back.jpg")
print("----")
api.book_bank_api("media/E7393203-15.jpg")
print("----")
taskGuid = api.face_liveness("media/passport.jpg")
api.info_face_liveness(taskGuid=str(taskGuid))
print("----")
api.signature_detect("media/signature.jpg")
print("----")
api.water_meter_binary("media/wm.jpg")
print("----")
api.thai_qa_api(headers={'Content-Type': 'application/json'}, question="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่", document="จังหวัดแค็วม์โปแลนด์คือหน่วยการปกครองท้องถิ่นของประเทศโปแลนด์ในช่วงปี ค.ศ.1975 - ค.ศ.1998 จังหวัดได้รับการรวมเข้ากับจังหวัดลูบลินมีเมืองหลักคือแค็วม์ใน ปี ค.ศ.1998 มีพื้นที่ประมาณ 3865 ตารางกิโลเมตรและมีประชากร 248800 คน")
print("----")
api.thai_asr_api("media/data.wav")
print("----")
api.thai_thaitts_kaitom("Hello")
print("----")
api.thai_thaitts_cee("Hello")
print("----")
#Change apikey to the invalid one.
# print(api.idcard_front("media/id-card-front.jpg", headers={"apikey":"123"}))