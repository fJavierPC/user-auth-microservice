from fastapi import FastAPI
from api.routes.auth_routes import router as auth_router
from api.routes.user_routes import router as user_router

app = FastAPI(
    title="Authentication Service",
    description="Documentación de la API con rutas organizadas en versiones",
    version="1.0.0"
)

# Incluir las rutas
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/v1/user", tags=["Users"])