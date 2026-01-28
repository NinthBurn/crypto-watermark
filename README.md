# API Watermarking – Front-End

Acest API permite încărcarea imaginilor, aplicarea watermark-ului și extragerea watermark-ului folosind metodele **DWT** sau **DCT** (DCT neimplementat încă).  

Toate request-urile trebuie să fie de tip **`multipart/form-data`**.

Pentru a rula server-ul: `uvicorn main:WatermarkAPI --reload`

Se acceseaza UI de pe `localhost:8000/frontend`

---

## 1️⃣ Endpoint: Upload imagine cu watermark

**URL:** `POST /images/upload/`

**Form-data fields:**

| Key             | Type | Description                          |
|-----------------|------|--------------------------------------|
| `file`          | File | Imaginea principală (jpg/png)        |
| `watermark_file`| File | Watermark-ul (jpg/png)               |
| `method`        | Text | Metoda de watermarking (`DWT` sau `DCT`) |

**Exemplu Postman:**

1. Select `Body` → `form-data`  
2. Adaugă trei câmpuri:
   - Key: `file` → Type: `File` → selectezi imaginea principală
   - Key: `watermark_file` → Type: `File` → selectezi watermark-ul
   - Key: `method` → Type: `Text` → Value: `DWT`
3. Trimite request-ul.  

**Răspuns:**  
- Returnează **fișierul watermarked** direct.  
- Numele fișierului returnat: `watermarked_<nume_fișier>`.  
- Tip media: același cu imaginea originală (jpg/png).

---

## 2️⃣ Endpoint: Extract Watermark

**URL:** `POST /images/extract-watermark/`

**Form-data fields:**

| Key                 | Type | Description                                  |
|--------------------|------|----------------------------------------------|
| `original_image`    | File | Imaginea originală (pentru DWT, păstrată)   |
| `watermarked_image` | File | Imaginea care conține watermark-ul          |
| `method`            | Text | Metoda folosită pentru watermark (`DWT`)    |

**Exemplu Postman:**

1. Select `Body` → `form-data`  
2. Adaugă trei câmpuri:
   - Key: `original_image` → Type: `File` → selectezi imaginea originală
   - Key: `watermarked_image` → Type: `File` → selectezi imaginea watermarked
   - Key: `method` → Type: `Text` → Value: `DWT`
3. Trimite request-ul.  

**Răspuns:**  
- Returnează **fișierul cu watermark-ul extras**.  
- Numele fișierului returnat: `extracted_<nume_fișier>`.  
- Tip media: același ca imaginea originală (jpg/png).  

---

### Observații:

- Pentru metoda DCT, endpointurile sunt pregătite, dar momentan nu sunt implementate.  
- Toate imaginile și watermark-urile trebuie să fie **PNG sau JPEG**.  
- Dimensiunea recomandată pentru imagini: între 256x256 px și 1024x1024 px.  
