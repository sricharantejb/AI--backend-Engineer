from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app);H={'Authorization':'Bearer demo-token'}
def test_health(): assert c.get('/health').status_code==200
def test_auth(): assert c.get('/widgets').status_code==401
def test_widget():
 r=c.post('/widgets',headers=H,json={'title':'Demo'});assert r.status_code==201;wid=r.json()['id'];assert c.get('/widgets/'+wid,headers=H).status_code==200;assert c.get('/widgets/'+wid+'/config').status_code==200
