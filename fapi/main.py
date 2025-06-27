from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fapi.routes.user_and_bd_routes import router as user_router
from fapi.routes.auth_routes import router as auth_router
from fapi.routes.location_routes import (router as locations_router,
                                         init_multiplex_client_loc,shutdown_multiplex_client_loc)
from fapi.routes.rec_route import router as rec_router
from .database import init_db
from fapi.routes.google_routes import (
    router as google_router,
    init_multiplex_client_google,
   shutdown_multiplex_client_google,
)





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
app.add_event_handler("startup", init_multiplex_client_loc)
app.add_event_handler("startup", init_multiplex_client_google)
app.add_event_handler("shutdown", shutdown_multiplex_client_loc)
app.add_event_handler("shutdown", shutdown_multiplex_client_google)
app.include_router(user_router, tags=["Users"])
app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(rec_router)
app.include_router(google_router, tags=["Google"])