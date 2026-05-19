import io
import base64
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ultralytics import YOLO
from PIL import Image
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uvicorn

app = FastAPI(title="API de Detecção de Cigarrinha", description="Detecta cigarrinhas em imagens usando um modelo personalizado treinado.")

# Configuração de autenticação (Google OAuth 2.0)
security = HTTPBearer()

# Carrega o modelo
model = YOLO("cigarrinha.pt")

# Função que valida o Token do Google
def verify_google_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Valida o token diretamente com o Google
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), audience=None)
        
        # Se o token for válido, podemos extrair as informações do usuário
        user_email = idinfo.get("email")
        return user_email
        
    except ValueError:
        # Se o token estiver expirado, for inválido ou adulterado, barramos aqui
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do Google inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/detect_cigarrinha")
async def detect_cigarrinha(file: UploadFile = File(...), user_email: str = Depends(verify_google_token)):
    # 1. Ler a imagem enviada
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    # 2. Rodar a inferência
    results = model.predict(img)
    result = results[0]
    
    # 3. Gerar a imagem marcada em Base64 para visualização
    im_array = result.plot()
    im_pil = Image.fromarray(im_array[..., ::-1])
    buffer = io.BytesIO()
    im_pil.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 4. Processar contagem e Formatar Coordenadas Estilo YOLO TXT
    coord = []
    counts = {}
    
    # boxes.cls: ID da classe
    # boxes.xywhn: coordenadas normalizadas (x_center, y_center, width, height)
    for box, cls in zip(result.boxes.xywhn, result.boxes.cls):
        class_id = int(cls)
        class_name = model.names[class_id]
        
        # Atualiza contagem por nome
        counts[class_name] = counts.get(class_name, 0) + 1
        
        # Formata coordenadas no formato YOLO: "class_id x_center y_center width height"
        line = f"{class_id} {box[0]:.8f} {box[1]:.8f} {box[2]:.8f} {box[3]:.8f}"
        coord.append(line)

    # 5. Retorno JSON
    return {
        "deteccoes": counts,
        "coordenadas": coord,
        "imagem_base64": img_str,
        "user_email": user_email
    }

@app.get("/model_cigarrinha_info")
async def get_model_cigarrinha_info(user_email: str = Depends(verify_google_token)):
    return {
        "model_name": "Detector de Cigarrinha",
        "classes": model.names, 
        "total_classes": len(model.names),
        "user_email": user_email
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)