from fastapi import FastAPI
from api.routes.auth_routes import router as auth_router

app = FastAPI()

# Incluir las rutas
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])