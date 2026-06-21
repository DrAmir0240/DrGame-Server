# users/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class PhoneRateThrottle(SimpleRateThrottle):
    rate = '100/hour'
    cache_format = 'throttle_phone_%(scope)s_%(ident)s'

    def get_cache_key(self, request, view):
        phone = request.data.get('phone')
        if not phone:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': phone
        }