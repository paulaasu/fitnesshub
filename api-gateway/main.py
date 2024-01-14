from fastapi import FastAPI, Request, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware

import httpx, os
from pydantic import BaseModel
from typing import Optional, List

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode


import requests

import jwt
import logging

from fastapi.responses import JSONResponse

import datetime

# Retrieve environment variables with default values
#TODO_SERVICE_URL = os.getenv('TODO_SERVICE_URL', 'http://localhost:8000')
MIC_USERS_URL = os.getenv('MIC_USERS_URL', 'http://localhost:3000/api/user')
EXERCISES_SERVICE_URL = os.getenv('EXERCISES_SERVICE_URL', 'http://localhost:8000/exercises/?muscle=')
TRAININGS_SERVICE_URL = os.getenv('TRAININGS_SERVICE_URL', 'http://localhost:8001')  



app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect root to index.html
@app.get("/")
async def read_root():
    return RedirectResponse(url="/static/index2.html")

client = httpx.Client()


# Models for user authentication
class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str
    #email: str

# Authentication endpoints
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    #print(f"{MIC_USERS_URL}/auth/register*************");
    response = client.post(f"{MIC_USERS_URL}/register", json=user.dict())
    if (response.status_code != 204 and response.headers["content-type"].strip().startswith("application/json")):
        try:
            return response.json()
        except ValueError:
            # decide how to handle a server that's misbehaving to this extent
            return {"message": response.text}
    return {"message": response.text}



@app.post("/auth/login")
async def login_user(user: UserLogin):
    print(f"{MIC_USERS_URL}/login")
    response = client.post(f"{MIC_USERS_URL}/login", json=user.dict())
    if (response.status_code != 400 and response.headers["content-type"].strip().startswith("application/json")):
        try:
            print(response.json())
            logged_in_user = response.json().get('user')
            token = response.json().get('token')  # Función para generar el token JWT
    
            return {"token": token, "user": logged_in_user}  # Retorna el token y la información del usuario
        except ValueError:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            print(f"Error al insertar la consulta del usuario: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    #return {"message": response.text}


@app.post("/auth/logout")
async def logout_user(user: UserLogin):
    try:
        response = client.post(f"{MIC_USERS_URL}/logout", json=user.dict())
        response.raise_for_status()  # Lanza una excepción para códigos de estado de error en la respuesta HTTP

        # Comprobación del tipo de contenido en la respuesta
        content_type = response.headers["content-type"].strip()
        if not content_type.startswith("application/json"):
            raise HTTPException(status_code=500, detail="Unexpected response content type")

        return {"message": "Logout successful"}  # Retorna un mensaje indicando que el logout fue exitoso

    except HTTPException as http_err:
        raise http_err  # Reenvía las excepciones de FastAPI directamente
    except Exception as e:
        print(f"Error al realizar la solicitud al servicio de usuarios: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class Exercise(BaseModel):
    name: str
    type: str
    muscle: str
    equipment: str
    difficulty: int
    instructions: str

EXTERNAL_API_URL = "https://exercisedb.p.rapidapi.com/exercises/bodyPart/back"
RAPIDAPI_KEY = "94413f86ffmshdb45fac8326cbc3p199823jsnd3f2ee75bef8"

@app.get("/exercises2/")
async def get_exercises(muscle: str = Query(..., title="Muscle")):
    try:
        if muscle:
            url = EXTERNAL_API_URL
            query_params = {"bodyPart": muscle, "limit": "10"}
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=query_params)

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch exercises. Status code: {response.status_code}"
                )
        else:
            raise HTTPException(status_code=400, detail="Missing muscle parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
RAPIDAPI_KEY = "94413f86ffmshdb45fac8326cbc3p199823jsnd3f2ee75bef8"
RAPIDAPI_HOST = "exercisedb.p.rapidapi.com"
  
@app.get("/exercises/name")
async def get_exercises_name(name: str = Query(..., title="Name")):
    try:
        if name:
            url = f"https://exercisedb.p.rapidapi.com/exercises/name/{name}"
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": RAPIDAPI_HOST
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch exercises. Status code: {response.status_code}"
                )
        else:
            raise HTTPException(status_code=400, detail="Missing name parameter")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ruta para obtener entrenamientos
@app.get("/trainings/")
async def get_trainings():
    try:
        #response = client.post(f"{TRAININGS_SERVICE_URL}/getTrainings")
        response = client.get("http://localhost:8001/getTrainings")
        print(response)
        response.raise_for_status()  # Lanza una excepción si la respuesta tiene un código de error
        trainings_data = response.json()
        return trainings_data
    except httpx.HTTPError as exc:
        logging.error(f"Error al llamar al servicio de entrenamientos: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Error en el servicio de entrenamientos: {str(exc)}")

# Proxy route for trainings service - GET a specific training
@app.get("/trainings/{training_id}")
async def training_service_proxy(training_id: int):
    try:
        response = await client.get(f"{TRAININGS_SERVICE_URL}/trainings/{training_id}")
        return JSONResponse(content=response.content, status_code=response.status_code, headers=response.headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
# Model for marking a training as completed
class MarkTrainingCompleted(BaseModel):
    user_id: int
    training_id: int


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Proxy route for marking a training as completed
@app.post("/trainings/completed")
async def mark_training_completed(data: MarkTrainingCompleted):
    try:
        
        print(f"{MIC_USERS_URL}/markCompletedTraining")
        # Hacer una solicitud al microservicio de usuarios para marcar el entrenamiento como completado
        response = client.post(f"{MIC_USERS_URL}/markCompletedTraining", json=data.dict())
        print(response)
        response.raise_for_status()

        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    

# Ruta para verificar si un usuario ha completado un entrenamiento específico
@app.post("/trainings/checkCompleted")
async def check_completed_training(data: MarkTrainingCompleted):
    try:
        print(f"{MIC_USERS_URL}/checkCompletedTraining")
        # Hacer una solicitud al microservicio de usuarios para verificar el entrenamiento completado
        response = client.post(f"{MIC_USERS_URL}/checkCompletedTraining", json=data.dict())
        print(response)
        response.raise_for_status()
        print(response.json())

        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.delete("/trainings/deleteCompletedTraining")
async def delete_completed_training(data: MarkTrainingCompleted):
    try:
        print(f"{MIC_USERS_URL}/deleteCompletedTraining")
       # response = client.delete("http://localhost:3000/api/user/deleteCompletedTraining", json=data.dict())
        response = client.request("DELETE", "http://localhost:3000/api/user/deleteCompletedTraining", json=data.dict())
        #response = client.post(f"{MIC_USERS_URL}/deleteCompletedTraining", json=data.dict())
        print(response)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
