from fastapi import Header,HTTPException
from app.core.config import DEMO_TOKEN
def current_tenant(authorization:str|None=Header(default=None)):
 if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Authentication required')
 if authorization[7:].strip()!=DEMO_TOKEN: raise HTTPException(401,'Invalid token')
 return 'demo-tenant'
