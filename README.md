Upload imagine cu watermark

Endpoint:
POST /images/upload/

Descriere:
Încarcă o imagine și o imagine de tip watermark, aplică watermarking folosind metoda selectată, calculează metricile PSNR și BER și salvează rezultatul în baza de date.

Tip request:
multipart/form-data

Câmpuri request:
	•	file (File, obligatoriu) – imaginea originală (PNG sau JPEG)
	•	watermark_file (File, obligatoriu) – imaginea watermark (PNG sau JPEG)
	•	method (String, obligatoriu) – metoda de watermarking (ex: DWT)

Răspuns (200 OK):

{
  "message": "Image uploaded, watermarked and saved successfully",
  "filename": "exemplu.jpg",
  "method": "DWT",
  "psnr": 41.09,
  "ber": 0.0,
  "width": 530,
  "height": 530,
  "format": "image/jpeg"
}

Erori posibile:
	•	400 Bad Request – format de imagine invalid, dimensiuni nepermise sau metodă de watermarking neacceptată.