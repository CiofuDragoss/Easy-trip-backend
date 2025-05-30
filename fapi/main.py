from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fapi.routes.user_routes import router as user_router
from fapi.routes.auth_routes import router as auth_router
from fapi.routes.location_routes import router as locations_router
from fapi.routes.shopping_routes import router as shopping_router
from .database import init_db
from fapi.routes.google_routes import router as google_router






app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(shopping_router)
app.include_router(google_router, tags=["Google"])