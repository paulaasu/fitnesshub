from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

# Define the microservices URLs
USER_SERVICE_URL = "http://localhost:3000"
EXERCISES_SERVICE_URL = "http://localhost:8000"
TRAININGS_SERVICE_URL = "http://localhost:8001"  
#WORKOUTS_SERVICE_URL = "http://fitnesshub-workouts-microservice:8003"

client = httpx.AsyncClient()

async def proxy_request(request: Request, service_url: str):
    method = request.method
    url = f"{service_url}{request.url.path}"
    headers = {key: value for key, value in request.headers.items()}
    content = await request.body()

    try:
        response = await client.request(method, url, headers=headers, content=content)
        return JSONResponse(content=response.content, status_code=response.status_code, headers=response.headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(path: str, request: Request):
    return await proxy_request(request, USER_SERVICE_URL)

# Proxy route for exercises service
@app.get("/exercises/")
async def exercises_service_proxy(muscle: str = Query(None)):
    path = f"?muscle={muscle}" if muscle else ""
    request = Request({})  # Asegurarse de que sea un objeto Request válido
    return await proxy_request(request, f"{EXERCISES_SERVICE_URL}{path}")


# Proxy route for trainings service - GET all trainings
@app.get("/trainings/{path:path}", methods=["GET"])
async def trainings_service_proxy():
    request = Request({})  # Asegurarse de que sea un objeto Request válido
    return await proxy_request(request, TRAININGS_SERVICE_URL)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway:app", host="0.0.0.0", port=8080, reload=True)
