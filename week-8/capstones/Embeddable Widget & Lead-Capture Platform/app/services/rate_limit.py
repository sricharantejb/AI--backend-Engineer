import time
from collections import defaultdict,deque
from fastapi import HTTPException
from app.core.config import RATE_LIMIT,RATE_WINDOW_SECONDS
hits=defaultdict(deque)
def check(key):
 q=hits[key]; now=time.time()
 while q and now-q[0]>RATE_WINDOW_SECONDS:q.popleft()
 if len(q)>=RATE_LIMIT:raise HTTPException(429,'Rate limit exceeded')
 q.append(now)
