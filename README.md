# API de Detecção de Cigarrinha

Bem-vindo à documentação da **API de Detecção de Cigarrinha**. Este projeto é um microsserviço hospedado localmente que utiliza inteligência artificial (modelos YOLO via Ultralytics) para analisar imagens, identificar espécies e retornar dados estruturados prontos para integração.

## Tecnologias Utilizadas
* **Python 3.x**
* **FastAPI:** Framework web de alta performance.
* **Ultralytics (YOLO):** Motor de inferência de visão computacional.
* **Google OAuth2:** Camada de autenticação e segurança.
* **Uvicorn:** Servidor ASGI para rodar a aplicação.

## Documentação dos Endpoints

### 1. Informações do Modelo
Retorna os metadados do modelo atualmente carregado na API e valida o usuário autenticado.

* **URL:** `/model_cigarrinha_info`
* **Método:** `GET`
* **Autenticação Exigida:** Sim (`Bearer Token`)

**Resposta de Sucesso (200 OK):**

Retorna um objeto JSON contendo o nome do modelo, o dicionário de classes disponíveis e o e-mail do usuário validado.

```json
{
    "model_name": "Detector de Cigarrinha",
    "classes": {
        "0": "cigarrinha"
    },
    "total_classes": 1,
    "user_email": "usuario@dominio.com"
}
```

### 2. Detecção em Imagem
Recebe uma imagem, executa a inferência usando o modelo YOLO e retorna a contagem, as coordenadas das caixas delimitadoras e a própria imagem processada.

* **URL:** `/detect_cigarrinha`
* **Método:** `POST`
* **Autenticação Exigida:** Sim (`Bearer Token`)

**Parâmetros da Requisição (Body):**
O corpo da requisição deve ser enviado no formato `multipart/form-data`.

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `file` | Arquivo | A imagem a ser processada (JPEG, PNG, etc). |

**Resposta de Sucesso (200 OK):**

Retorna um objeto JSON com o resumo das detecções, as coordenadas no padrão YOLO (TXT), a imagem resultante em Base64 e o usuário que solicitou o processamento.

```json
{
    "deteccoes": {
        "cigarrinha": 3
    },
    "coordenadas": [
        "0 0.83750000 0.39062500 0.03593750 0.04062500",
        "0 0.62031250 0.36406250 0.03828125 0.04453125",
        "0 0.66406250 0.53046875 0.02343750 0.06328125"
    ],
    "imagem_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAA...",
    "user_email": "usuario@dominio.com"
}
```

## Como Testar a API Localmente

Esta API utiliza **Google OAuth2** para segurança. Para testar os endpoints de detecção (`/detect_cigarrinha`) e informações do modelo (`/model_cigarrinha_info`), você precisará fornecer um Token de autenticação válido em cada requisição.

### 1. Obtendo um Token de Teste Temporário
Para facilitar o desenvolvimento, você pode gerar um token de teste oficial do Google que dura 1 hora:

1. Acesse o [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground).
2. Na coluna da esquerda (**Step 1**), procure e clique em **Google OAuth2 API v2**.
3. Marque a opção `https://www.googleapis.com/auth/userinfo.email`.
4. Clique no botão azul **Authorize APIs** e faça login com sua conta Google.
5. Em **Step 2**, clique no botão azul **Exchange authorization code for tokens**.
6. Copie todo o texto contido no campo **ID Token** (é uma string longa). Este é o seu token de acesso.

---

### 2. Testando via Interface Gráfica (Swagger)
O FastAPI gera uma interface amigável para testar o envio de imagens diretamente pelo navegador:

1. Com a API rodando no terminal (`python main.py`), abra o navegador e acesse: [http://localhost:8000/docs](http://localhost:8000/docs)
2. No canto superior direito da página, clique no botão **Authorize** (ícone de cadeado).
3. No campo que aparecer, cole o seu **ID Token** e clique em **Authorize**. Depois, feche a janelinha.
4. Clique no endpoint azul `POST /detect_cigarrinha` para expandi-lo.
5. Clique em **Try it out**.
6. No campo `file`, selecione uma imagem de teste do seu computador.
7. Clique em **Execute**.
8. A resposta detalhada aparecerá abaixo, contendo a contagem das classes, as coordenadas (padrão YOLO) e a imagem processada em Base64.

---

### 3. Testando via Terminal (cURL)
Se você preferir automatizar ou testar via linha de comando, utilize o `cURL`. 

Substitua `SEU_ID_TOKEN_AQUI` pelo token copiado no Passo 1 e `/caminho/para/imagem.jpg` pelo local real da foto no seu computador:

```bash
curl -X 'POST' \
  'http://localhost:8000/detect_cigarrinha' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_ID_TOKEN_AQUI' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/caminho/para/imagem.jpg;type=image/jpeg'