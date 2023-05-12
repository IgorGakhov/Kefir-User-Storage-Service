from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.core.handlers import \
    internal_exception_handler, client_http_exception_handler
from src.auth.router import router as router_auth
from src.users.router import router_users, router_admin


app = FastAPI(
    title='Kefir Python Junior Test',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    status.HTTP_500_INTERNAL_SERVER_ERROR, internal_exception_handler
)
app.add_exception_handler(HTTPException, client_http_exception_handler)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_admin)


if __name__ == "__main__":
    uvicorn.run(app)
