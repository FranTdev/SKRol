from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth

app = FastAPI(title="Stephen King RPG API")

# Configurar CORS (Para que tu Web pueda hablar con el Backend)
# Esto permite que tu HTML local o Unity se conecten sin errores de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambia "*" por tu dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de autenticación
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

@app.get("/")
def read_root():
    return {"message": "El servidor del RPG está funcionando. Todo sirve al Haz."}