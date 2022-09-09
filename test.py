# -*- coding: utf-8 -*-
#Example

import iapp_ai
################## api key ##################

api = iapp_ai.api("rL3eZA5M3Or78dKgYWtXh3EDylXpao68")

# Normal usage

################## Thai Natural Language Processing ##################

# api.thai_text_summarization(text="ตำรวจกองปราบ ดังกล่าวล่าสุด เมื่อเวลา 09.30 น. วันที่ 11 มีนาคม 2555 ผู้สื่อข่าวรายงานว่า ภายหลัง พล.ต.ท.จิรภพ ภูริเดช ผบช.ก. นำกําลังตำรวจสอบสวนกลาง สนธิกำลังร่วมกับ ตำรวจภูธรภาค 9 เข้าตรวจค้นพื้นที่เป้าหมายหลายจุดเมื่อช่วงเช้าที่ผ่านมา สุดขณะนี้ สามารถจับกุมตัว นายพงศกร หรือเจ สุวรรณมะโณ อายุ 22 ปี หนึ่งในกลุ่มผู้ต้องหาที่ถูกออกหมายจับได้ หลังทราบว่าหลบซ่อนตัวอยู่ภายในพื้นที่ อ.รัตภูมิ จ.สงขลา ก่อนพาตัวเข้าจุดซ่อนอาวุธปืนภายในสวนปาล์มท้ายวัดท่าควาย ซึ่งจากการหาเข้าตรวจค้น พบอาวุธปืนในการก่อเหตุจํานวน 2 กระบอก ประกอบด้วย ปีนเอชเค 1 กระบอก และ ปืนพกสั้นขนาด 9 มม. 1 กระบอก ซุกซ่อนในกอหญ้าในต้นปาล์มและต้นกล้วย", output_length=84)
# api.thai_qa_api(question="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่", document="จังหวัดแค็วม์โปแลนด์คือหน่วยการปกครองท้องถิ่นของประเทศโปแลนด์ในช่วงปี ค.ศ.1975 - ค.ศ.1998 จังหวัดได้รับการรวมเข้ากับจังหวัดลูบลินมีเมืองหลักคือแค็วม์ใน ปี ค.ศ.1998 มีพื้นที่ประมาณ 3865 ตารางกิโลเมตรและมีประชากร 248800 คน")
# api.thai_qgen_api(text="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่")
# api.eng_thai_translate(text="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่")
# api.thai_text_parser(text="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่")
################## Image Recognition ##################

# api.idcard_front("media/id-card-front.jpg")

# api.idcard_back("media/id-card-back.jpg")

# api.license_plate_ocr("media/plate.jpg")

# api.book_bank_api("media/1.jpg")

# api.passport_ocr("media/ukr-passport.jpeg")

# api.document_ocr_plaintext("media/pdf02.pdf")
# api.document_ocr_json_layout("media/pdf02.pdf")
api.document_ocr_docx("media/pdf02.pdf")

# api.signature_detect("media/signature.jpg")

# api.power_meter(headers={'Content-Type': 'application/json'}, image="media/base64.txt")

# # api.water_meter_binary("media/wm.jpg")
# api.water_meter_base64(image="media/water-meter.txt")
# api.img_bg_removal("media/base64.txt")

# taskGuid = api.face_liveness("media/face.jpg")
# i = 1
# while i != 0 :
#     info = api.info_face_liveness(taskGuid=str(taskGuid).replace('"',''))
#     a_dict=info.json()
#     for key,value in a_dict.items():
#         if key == "status" and value == 'C':
#             print(a_dict)
#             i -= 1

# api.face_verification("media/id-card-front.jpg", "media/id-card-front.jpg", "iApp", "0.1")
# api.face_ver_config_score("0.5","0.5","iApp", "iApp")
# api.face_ver2("media/face.jpg", "media/face.jpg")

# api.face_detect_single("media/face.jpg")
# api.face_detect_multi("media/multi_face.jpg", "iApp")
# api.face_detect_config_score("0.5","iApp", "iApp")

# api.face_recog_single("media/face.jpg", "iApp")
# api.face_recog_multi("media/multi_face.jpg", "iApp")
# api.face_recog_facecrop("media/face.jpg", "iApp")
# api.face_recog_add("media/face.jpg", "iApp", "Panuphong", "iApp")
# api.face_recog_import("media/file.csv", "iApp", "iApp")
# api.face_recog_check("iApp", "iApp")
# api.face_recog_export("iApp", "iApp", "excel")
# api.face_recog_remove("iApp", "Panupong", "iApp", "05-08-2022", "1")
# api.face_recog_config_score("0.9", "0.5","iApp", "iApp")

################## Voice and Speech ##################

# api.thai_asr_api("media/2ppl.wav")
# api.thai_thaitts_kaitom("Hello")
# api.thai_thaitts_cee("Hello")

################## Optimization and Prediction ##################
""" Avaible Soon: Automatic Route Optimization, Stock Trading Prediction """


#Change apikey to the invalid one.
# print(api.idcard_front("media/id-card-front.jpg", headers={"apikey":"123"}))