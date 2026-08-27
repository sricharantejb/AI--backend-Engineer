import logging
log=logging.getLogger(__name__)
def send_confirmation(payload):
 try:
  if payload.get('_force_side_effect_failure'):raise RuntimeError('simulated failure')
  log.info('Confirmation side effect: %s',payload)
 except Exception:log.exception('Non-critical side effect failed')
