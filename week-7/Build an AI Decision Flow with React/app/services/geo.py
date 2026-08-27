import requests
def provider_a(ip):
 if ip in ('127.0.0.1','::1','test'):return {'country':'Local','city':'Localhost'}
 r=requests.get(f'https://ip-api.com/json/{ip}?fields=status,country,city',timeout=2); d=r.json()
 if d.get('status')!='success':raise RuntimeError('provider A failed')
 return {'country':d.get('country'),'city':d.get('city')}
def provider_b(ip):
 r=requests.get(f'https://ipapi.co/{ip}/json/',timeout=2); d=r.json()
 if d.get('error'):raise RuntimeError('provider B failed')
 return {'country':d.get('country_name'),'city':d.get('city')}
def enrich(ip):
 try:return provider_a(ip)
 except Exception:
  try:return provider_b(ip)
  except Exception:return {'country':None,'city':None}
