import io
import base64
import json
import uvicorn
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ultralytics import YOLO
from PIL import Image
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from database import engine, Base, SessionLocal, User, APILog

# ==========================================
# CONFIGURAÇÃO INICIALIZAÇÃO 
# ==========================================

# Cria as tabelas no banco de dados automaticamente ao iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Detecção de Cigarrinha", description="Detecta cigarrinhas em imagens usando um modelo personalizado treinado.")

# Dependência para injetar a sessão do banco em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Carrega o modelo
model = YOLO("cigarrinha.pt")

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA 
# ==========================================

SECRET_KEY = "CIA-AGRO@2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

def get_password_hash(password: str) -> str:
    # Transforma a senha em bytes, gera o salt e o hash
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compara a senha digitada com o hash salvo
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# ==========================================
# ROTAS DA API
# ==========================================

class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "Usuário criado com sucesso!"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.email})
    new_token_log = APILog(user_id=user.id, endpoint="/token", resposta_json=json.dumps({"login": "success", "timestamp": datetime.utcnow().isoformat()}))
    db.add(new_token_log)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/detect_cigarrinha")
async def detect_cigarrinha(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ler a imagem enviada
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    # Rodar a inferência
    results = model.predict(img)
    result = results[0]
    
    # Gerar a imagem marcada em Base64 para visualização
    im_array = result.plot()
    im_pil = Image.fromarray(im_array[..., ::-1])
    buffer = io.BytesIO()
    im_pil.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Processar contagem e Formatar Coordenadas Estilo YOLO TXT
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

    # Salva o log no banco de dados separado
    resumo_log = {"deteccoes": counts, "coordenadas": len(coord), "timestamp": datetime.utcnow().isoformat(), "imagem": file.filename}
    novo_log = APILog(user_id=current_user.id, endpoint="/detect_cigarrinha", resposta_json=json.dumps(resumo_log))
    db.add(novo_log)
    db.commit()

    # Retorno JSON
    return {
        "deteccoes": counts,
        "coordenadas": coord,
        "imagem_base64": img_str,
        "user_email": current_user.email
    }

@app.get("/model_cigarrinha_info")
async def get_model_cigarrinha_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Salva o log no banco de dados separado
    resumo_log = {"model_info": {"classes": model.names, "total_classes": len(model.names)}, "timestamp": datetime.utcnow().isoformat()}
    novo_log = APILog(
        user_id=current_user.id,
        endpoint="/model_cigarrinha_info",
        resposta_json=json.dumps(resumo_log)
    )
    db.add(novo_log)
    db.commit()
    
    return {
        "model_name": "Detector de Cigarrinha",
        "classes": model.names, 
        "total_classes": len(model.names),
        "user_email": current_user.email
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)