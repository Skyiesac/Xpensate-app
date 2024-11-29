from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# User Rate Throttles
class AnonUserRateThrottle(AnonRateThrottle):
    scope = "anonotp"

class KnownUserRateThrottle(UserRateThrottle):
    scope = "userotp"