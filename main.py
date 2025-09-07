from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

UPLOAD_DIR = "uploaded_images"

load_dotenv()
API_PASSWORD = os.getenv("API_PASSWORD")
app = FastAPI()

# Garante que a pasta existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Função de dependência para checar senha
def check_password(x_api_key: str = Header(...)):
    if x_api_key != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha inválida")

# Endpoint para upload de imagem
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), auth=Depends(check_password)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo não é uma imagem")
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

# Endpoint para listar imagens
@app.get("/images")
def list_images(auth=Depends(check_password)):
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return JSONResponse(files)

# Endpoint para servir imagens
@app.get("/images/{image_name}")
def get_image(image_name: str, auth=Depends(check_password)):
    file_path = os.path.join(UPLOAD_DIR, image_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(file_path)

# Servir arquivos estáticos (opcional)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
