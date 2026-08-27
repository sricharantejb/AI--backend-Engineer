from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
app=FastAPI(title='FlyRank Embeddable Widget & Lead-Capture Platform',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
app.include_router(router)
@app.get('/health')
def health(): return {'status':'ok'}
