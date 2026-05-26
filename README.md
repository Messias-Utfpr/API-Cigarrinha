# API de Detecção de Cigarrinha

API desenvolvida com FastAPI + YOLO para detecção de cigarrinhas em imagens utilizando autenticação JWT, banco de dados SQLAlchemy e controle de usuários.

---

# Funcionalidades

- Cadastro de usuários
- Login com JWT Bearer Token
- Detecção de cigarrinhas utilizando YOLO
- Retorno da imagem anotada em Base64
- Coordenadas no formato YOLO TXT
- Registro de logs das requisições no banco de dados
- Documentação automática Swagger

---

# Tecnologias Utilizadas

- FastAPI
- YOLO (Ultralytics)
- SQLAlchemy
- JWT Authentication
- Passlib / Bcrypt
- Pillow
- Uvicorn

---

# Estrutura da API

## Base URL

```txt
http://SEU_SERVIDOR:8000
```

Exemplo:

```txt
http://127.0.0.1:8000
```

---

# Autenticação

A autenticação é realizada utilizando JWT Bearer Token.

Fluxo:

1. Registrar usuário
2. Realizar login
3. Utilizar o token retornado nas próximas requisições

---

# Cadastro de Usuário

Cria um novo usuário na plataforma.

## Endpoint

```http
POST /register
```

---

## Body JSON

```json
{
  "email": "usuario@gmail.com",
  "password": "123456"
}
```

---

## Exemplo CURL

```bash
curl -X POST "http://127.0.0.1:8000/register" \
-H "Content-Type: application/json" \
-d "{\"email\":\"usuario@gmail.com\",\"password\":\"123456\"}"
```

---

## Resposta

```json
{
  "message": "Usuário criado com sucesso!"
}
```

---

# Login

Realiza autenticação e retorna o JWT Token.

## Endpoint

```http
POST /token
```

---

## Content-Type

```http
application/x-www-form-urlencoded
```

---

## Parâmetros

| Campo | Valor |
|---|---|
| username | email do usuário |
| password | senha do usuário |

---

## Exemplo CURL

```bash
curl -X POST "http://127.0.0.1:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=usuario@gmail.com&password=123456"
```

---

## Exemplo de Resposta

```json
{
  "access_token": "SEU_TOKEN_JWT",
  "token_type": "bearer"
}
```

---

# Utilizando o Token

Após realizar o login, envie o token no header Authorization:

```http
Authorization: Bearer SEU_TOKEN_JWT
```

---

# Endpoint: Detectar Cigarrinhas

Realiza a detecção de cigarrinhas em uma imagem.

## Endpoint

```http
POST /detect_cigarrinha
```

---

## Headers

```http
Authorization: Bearer SEU_TOKEN_JWT
Content-Type: multipart/form-data
```

---

## Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| file | imagem | Sim | Imagem para análise |

---

## Exemplo CURL

```bash
curl -X POST "http://127.0.0.1:8000/detect_cigarrinha" \
-H "Authorization: Bearer SEU_TOKEN_JWT" \
-F "file=@imagem.jpg"
```

---

## Exemplo de Resposta

```json
{
  "deteccoes": {
    "cigarrinha": 3
  },
  "coordenadas": [
    "0 0.51234567 0.42123456 0.10234567 0.08234567",
    "0 0.71234567 0.32123456 0.09234567 0.07234567"
  ],
  "imagem_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "user_email": "usuario@gmail.com"
}
```

---

# Campos da Resposta

| Campo | Descrição |
|---|---|
| deteccoes | Quantidade detectada por classe |
| coordenadas | Coordenadas no formato YOLO TXT |
| imagem_base64 | Imagem anotada em Base64 |
| user_email | Usuário autenticado |

---

# Endpoint: Informações do Modelo

Retorna informações do modelo carregado.

## Endpoint

```http
GET /model_cigarrinha_info
```

---

## Headers

```http
Authorization: Bearer SEU_TOKEN_JWT
```

---

## Exemplo CURL

```bash
curl -X GET "http://127.0.0.1:8000/model_cigarrinha_info" \
-H "Authorization: Bearer SEU_TOKEN_JWT"
```

---

## Exemplo de Resposta

```json
{
  "model_name": "Detector de Cigarrinha",
  "classes": {
    "0": "cigarrinha"
  },
  "total_classes": 1,
  "user_email": "usuario@gmail.com"
}
```

---

# Sistema de Logs

Todas as chamadas autenticadas dos endpoints principais são registradas automaticamente no banco de dados.

Os logs armazenam:

- Usuário responsável
- Endpoint acessado
- Resumo da resposta
- Timestamp da requisição

---

# Banco de Dados

As tabelas são criadas automaticamente ao iniciar a aplicação:

```python
Base.metadata.create_all(bind=engine)
```

---

# Executando Localmente

## Instalar Dependências

```bash
pip install fastapi uvicorn ultralytics pillow sqlalchemy passlib bcrypt pyjwt python-multipart
```

---

## Executar Aplicação

```bash
python main.py
```

ou

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

# Documentação Automática

O FastAPI gera automaticamente a documentação Swagger.

## Swagger UI

```txt
http://127.0.0.1:8000/docs
```

---

# Segurança

- Senhas criptografadas com Bcrypt
- Autenticação JWT
- Tokens com expiração automática
- Rotas protegidas com Bearer Token

---

# Estrutura do Projeto

```txt
.
├── app.py
├── database.py
├── cigarrinha.pt
├── cigarrinha.onnx
├── requirements.txt
└── database.db
```

---

# Exemplo Completo de Fluxo

## 1. Registrar usuário

```bash
curl -X POST "http://127.0.0.1:8000/register" \
-H "Content-Type: application/json" \
-d "{\"email\":\"usuario@gmail.com\",\"password\":\"123456\"}"
```

---

## 2. Fazer login

```bash
curl -X POST "http://127.0.0.1:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=usuario@gmail.com&password=123456"
```

---

## 3. Copiar o token retornado

```json
{
  "access_token": "TOKEN_AQUI",
  "token_type": "bearer"
}
```

---

## 4. Enviar imagem para detecção

```bash
curl -X POST "http://127.0.0.1:8000/detect_cigarrinha" \
-H "Authorization: Bearer TOKEN_AQUI" \
-F "file=@imagem.jpg"
```
