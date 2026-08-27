import json,os
from fastapi import APIRouter,Depends,HTTPException,Request,Response
from app.schemas.models import WidgetCreate,WidgetUpdate,Submission
from app.middleware.auth import current_tenant
from app.models.db import get_conn,init_db,new_id,now,row_to_dict
from app.services.rate_limit import check
from app.services.geo import enrich
from app.services.side_effects import send_confirmation
from app.core.config import APP_BASE_URL
router=APIRouter(); init_db()
def owned(conn,wid,tenant): return conn.execute('SELECT * FROM widgets WHERE id=? AND tenant_id=?',(wid,tenant)).fetchone()
@router.post('/widgets',status_code=201)
def create(b:WidgetCreate,tenant=Depends(current_tenant)):
 wid=new_id();t=now();c=get_conn();c.execute('INSERT INTO widgets VALUES(?,?,?,?,?,?,?,?,?,?,?)',(wid,tenant,b.type,b.title,b.description,json.dumps(b.fields),b.button_text,json.dumps(b.display_options),1,t,t));c.commit();r=c.execute('SELECT * FROM widgets WHERE id=?',(wid,)).fetchone();c.close();return {**row_to_dict(r),'embed_snippet':f'<script src="{APP_BASE_URL}/widget.v1.js?id={wid}"></script>'}
@router.get('/widgets')
def list_(tenant=Depends(current_tenant)):
 c=get_conn();r=c.execute('SELECT * FROM widgets WHERE tenant_id=? ORDER BY created_at DESC',(tenant,)).fetchall();c.close();return [row_to_dict(x) for x in r]
@router.get('/widgets/{wid}')
def get_(wid:str,tenant=Depends(current_tenant)):
 c=get_conn();r=owned(c,wid,tenant);c.close()
 if not r:raise HTTPException(404,'Widget not found')
 return row_to_dict(r)
@router.patch('/widgets/{wid}')
def update(wid:str,b:WidgetUpdate,tenant=Depends(current_tenant)):
 c=get_conn();r=owned(c,wid,tenant)
 if not r:c.close();raise HTTPException(404,'Widget not found')
 d=row_to_dict(r);d.update(b.model_dump(exclude_unset=True));v=d['version']+1;c.execute('UPDATE widgets SET type=?,title=?,description=?,fields_json=?,button_text=?,display_options_json=?,version=?,updated_at=? WHERE id=? AND tenant_id=?',(d['type'],d['title'],d['description'],json.dumps(d['fields']),d['button_text'],json.dumps(d['display_options']),v,now(),wid,tenant));c.commit();r=c.execute('SELECT * FROM widgets WHERE id=?',(wid,)).fetchone();c.close();return row_to_dict(r)
@router.delete('/widgets/{wid}',status_code=204)
def delete(wid:str,tenant=Depends(current_tenant)):
 c=get_conn();x=c.execute('DELETE FROM widgets WHERE id=? AND tenant_id=?',(wid,tenant));c.commit();c.close()
 if not x.rowcount:raise HTTPException(404,'Widget not found')
 return Response(status_code=204)
@router.get('/widgets/{wid}/embed')
def embed(wid:str,tenant=Depends(current_tenant)):
 c=get_conn();r=owned(c,wid,tenant);c.close()
 if not r:raise HTTPException(404,'Widget not found')
 return {'snippet':f'<script src="{APP_BASE_URL}/widget.v{r["version"]}.js?id={wid}"></script>'}
@router.get('/widgets/{wid}/config')
def config(wid:str):
 c=get_conn();r=c.execute('SELECT * FROM widgets WHERE id=?',(wid,)).fetchone();c.close()
 if not r:raise HTTPException(404,'Widget not found')
 d=row_to_dict(r);return Response(json.dumps({k:d[k] for k in ['id','type','title','description','fields','button_text','display_options']}),media_type='application/json',headers={'Cache-Control':'public, max-age=60'})
@router.get('/widget.v1.js')
def js(id:str):
 with open('static/widget.v1.js',encoding='utf8') as f:s=f.read()
 return Response(s,media_type='application/javascript',headers={'Cache-Control':'public, max-age=31536000, immutable'})
@router.post('/submissions',status_code=201)
def submit(b:Submission,request:Request,widget_id:str):
 ip=request.client.host if request.client else 'unknown';check(f'{ip}:{widget_id}')
 if b.honeypot:return {'status':'accepted'}
 c=get_conn();r=c.execute('SELECT * FROM widgets WHERE id=?',(widget_id,)).fetchone()
 if not r:c.close();raise HTTPException(404,'Widget not found')
 w=row_to_dict(r)
 for f in w['fields']:
  if f.get('required') and not b.data.get(f.get('name')):c.close();raise HTTPException(400,f"Missing required field: {f.get('name')}")
 if len(json.dumps(b.data))>10000:c.close();raise HTTPException(413,'Payload too large')
 geo=enrich(ip);sid=new_id();c.execute('INSERT INTO submissions VALUES(?,?,?,?,?,?,?,?)',(sid,widget_id,w['tenant_id'],json.dumps(b.data),ip,geo['country'],geo['city'],now()));c.commit();c.close();send_confirmation(b.data);return {'id':sid,'status':'stored','geo':geo}
@router.get('/dashboard/submissions')
def submissions(tenant=Depends(current_tenant)):
 c=get_conn();r=c.execute('SELECT s.*,w.title FROM submissions s JOIN widgets w ON w.id=s.widget_id WHERE s.tenant_id=? ORDER BY s.created_at DESC',(tenant,)).fetchall();c.close();return [dict(x)|{'data':json.loads(x['payload_json'])} for x in r]
@router.get('/dashboard/stats')
def stats(tenant=Depends(current_tenant)):
 c=get_conn();n=c.execute('SELECT COUNT(*) c FROM submissions WHERE tenant_id=?',(tenant,)).fetchone()['c'];w=c.execute('SELECT COUNT(*) c FROM widgets WHERE tenant_id=?',(tenant,)).fetchone()['c'];g=c.execute('SELECT country,COUNT(*) c FROM submissions WHERE tenant_id=? GROUP BY country',(tenant,)).fetchall();c.close();return {'widgets':w,'submissions':n,'geo_breakdown':[dict(x) for x in g]}
