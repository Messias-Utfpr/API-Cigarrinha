import io
import base64
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from PIL import Image
import uvicorn

app = FastAPI(title="API de Detecção de Cigarrinha", description="Detecta cigarrinhas em imagens usando um modelo personalizado treinado.")

# Carrega o modelo
model = YOLO("cigarrinha.pt")

@app.post("/detect_cigarrinha")
async def detect_cigarrinha(file: UploadFile = File(...)):
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
        "imagem_base64": img_str
    }

@app.get("/model_cigarrinha_info")
async def get_model_cigarrinha_info():
    return {
        "model_name": "Detector de Cigarrinha",
        "classes": model.names, 
        "total_classes": len(model.names)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)