POST /images/upload/

Încarcă o imagine PNG/JPEG și salvează un record în baza de date.

Body (form-data):

Field	Type	Description
file	File	Imagine PNG sau JPEG
method	Text	Metoda de watermarking (ex: DCT)

Exemplu curl:

curl -X POST "http://127.0.0.1:8000/images/upload/" \
  -F "file=@/cale/catre/imagine.png" \
  -F "method=DCT"

Răspuns:

{
  "message": "Image uploaded and saved successfully"
}

Erori:
	•	Format invalid: "Image must be PNG or JPEG"
	•	Dimensiune prea mică: "Image too small"
	•	Dimensiune prea mare: "Image too large"
