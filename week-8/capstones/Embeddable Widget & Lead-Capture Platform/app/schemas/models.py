from pydantic import BaseModel,Field,field_validator
from typing import Any,Dict,List,Optional,Literal
class WidgetCreate(BaseModel):
 type:Literal['signup','contact','cta','popover']='signup'; title:str=Field(...,min_length=1,max_length=120); description:str=Field('',max_length=500); fields:List[Dict[str,Any]]=Field(default_factory=lambda:[{'name':'email','type':'email','required':True}],max_length=20); button_text:str=Field('Submit',min_length=1,max_length=50); display_options:Dict[str,Any]=Field(default_factory=dict)
class WidgetUpdate(BaseModel):
 type:Optional[Literal['signup','contact','cta','popover']]=None; title:Optional[str]=Field(None,min_length=1,max_length=120); description:Optional[str]=Field(None,max_length=500); fields:Optional[List[Dict[str,Any]]]=Field(None,max_length=20); button_text:Optional[str]=Field(None,min_length=1,max_length=50); display_options:Optional[Dict[str,Any]]=None
class Submission(BaseModel):
 data:Dict[str,Any]=Field(default_factory=dict); honeypot:str=Field('',max_length=200)
 @field_validator('data')
 @classmethod
 def size(cls,v):
  if len(str(v))>10000: raise ValueError('Payload too large')
  return v
