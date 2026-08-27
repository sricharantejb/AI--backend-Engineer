import sqlite3, json, uuid
from datetime import datetime,timezone
from app.core.config import DATABASE_URL
DB_PATH=DATABASE_URL.replace('sqlite:///','') if DATABASE_URL.startswith('sqlite:///') else './data.db'
def get_conn():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
 c=get_conn(); c.executescript('''CREATE TABLE IF NOT EXISTS widgets(id TEXT PRIMARY KEY,tenant_id TEXT NOT NULL,type TEXT NOT NULL,title TEXT NOT NULL,description TEXT DEFAULT '',fields_json TEXT NOT NULL,button_text TEXT NOT NULL,display_options_json TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,updated_at TEXT NOT NULL); CREATE INDEX IF NOT EXISTS idx_widgets_tenant ON widgets(tenant_id); CREATE TABLE IF NOT EXISTS submissions(id TEXT PRIMARY KEY,widget_id TEXT NOT NULL,tenant_id TEXT NOT NULL,payload_json TEXT NOT NULL,ip TEXT,country TEXT,city TEXT,created_at TEXT NOT NULL); CREATE INDEX IF NOT EXISTS idx_submissions_tenant ON submissions(tenant_id); CREATE INDEX IF NOT EXISTS idx_submissions_widget ON submissions(widget_id);'''); c.commit(); c.close()
def now(): return datetime.now(timezone.utc).isoformat()
def new_id(): return str(uuid.uuid4())
def row_to_dict(row):
 if not row:return None
 d=dict(row); d['fields']=json.loads(d.pop('fields_json')); d['display_options']=json.loads(d.pop('display_options_json')); return d
