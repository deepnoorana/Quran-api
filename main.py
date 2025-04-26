from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# تحميل البيانات
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# بيانات دخول المشرف (مؤقتة هنا)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# التحقق من تسجيل الدخول
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", response_class=HTMLResponse)
async def root():
    return {"message": "Welcome to Quran API"}

@app.get("/surahs")
def get_surahs():
    data = load_data()
    return {id: surah["name"] for id, surah in data["surahs"].items()}

@app.get("/surahs/{surah_id}")
def get_surah(surah_id: int):
    data = load_data()
    surah = data["surahs"].get(str(surah_id))
    if not surah:
        raise HTTPException(status_code=404, detail="سورة غير موجودة")
    return surah

@app.get("/ayah/{surah_id}/{ayah_number}")
def get_ayah(surah_id: int, ayah_number: int):
    data = load_data()
    surah = data["surahs"].get(str(surah_id))
    if not surah or str(ayah_number) not in surah["ayahs"]:
        raise HTTPException(status_code=404, detail="آية غير موجودة")
    return {"surah": surah["name"], "ayah": surah["ayahs"][str(ayah_number)]}

# إدارة - إضافة سورة جديدة
@app.post("/admin/surah", dependencies=[Depends(verify_admin)])
def add_surah(id: int, name: str):
    data = load_data()
    if str(id) in data["surahs"]:
        raise HTTPException(status_code=400, detail="السورة موجودة بالفعل")
    data["surahs"][str(id)] = {"name": name, "ayahs": {}}
    save_data(data)
    return {"message": "تمت إضافة السورة"}

# إدارة - إضافة آية جديدة
@app.post("/admin/ayah", dependencies=[Depends(verify_admin)])
def add_ayah(surah_id: int, ayah_number: int, text: str):
    data = load_data()
    surah = data["surahs"].get(str(surah_id))
    if not surah:
        raise HTTPException(status_code=404, detail="سورة غير موجودة")
    surah["ayahs"][str(ayah_number)] = text
    save_data(data)
    return {"message": "تمت إضافة الآية"}

# إدارة - تعديل آية
@app.put("/admin/ayah/{surah_id}/{ayah_number}", dependencies=[Depends(verify_admin)])
def edit_ayah(surah_id: int, ayah_number: int, text: str):
    data = load_data()
    surah = data["surahs"].get(str(surah_id))
    if not surah or str(ayah_number) not in surah["ayahs"]:
        raise HTTPException(status_code=404, detail="آية غير موجودة")
    surah["ayahs"][str(ayah_number)] = text
    save_data(data)
    return {"message": "تم تعديل الآية"}

# إدارة - حذف آية
@app.delete("/admin/ayah/{surah_id}/{ayah_number}", dependencies=[Depends(verify_admin)])
def delete_ayah(surah_id: int, ayah_number: int):
    data = load_data()
    surah = data["surahs"].get(str(surah_id))
    if not surah or str(ayah_number) not in surah["ayahs"]:
        raise HTTPException(status_code=404, detail="آية غير موجودة")
    del surah["ayahs"][str(ayah_number)]
    save_data(data)
    return {"message": "تم حذف الآية"}