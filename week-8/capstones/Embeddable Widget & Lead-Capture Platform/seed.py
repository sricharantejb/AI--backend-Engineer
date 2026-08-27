import json
from app.models.db import *
init_db();c=get_conn();wid=new_id();t=now();c.execute('INSERT INTO widgets VALUES(?,?,?,?,?,?,?,?,?,?,?)',(wid,'demo-tenant','signup','Demo Lead Form','Capture a lead.',json.dumps([{'name':'name','type':'text','required':True},{'name':'email','type':'email','required':True}]),'Send',json.dumps({}),1,t,t));c.commit();c.close();print('Widget ID:',wid)
