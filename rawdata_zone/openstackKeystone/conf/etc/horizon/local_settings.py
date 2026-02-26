OPENSTACK_KEYSTONE_URL = "http://10.5.3.1:5000/v3"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "Default"
ALLOWED_HOSTS = ['*']
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '10.5.3.4:11211',  # Or your memcached host:port, e.g., 'memcached:11211' in containers
        # For multiple servers: 'LOCATION': ['host1:11211', 'host2:11211'],
        # Optional settings:
        # 'TIMEOUT': 300,
        # 'OPTIONS': {'tcp_nodelay': True},
    }
}

# If sessions explicitly reference a cache alias:
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Or 'cached_db' if you want DB fallback
SESSION_CACHE_ALIAS = 'default'

# WEBSSO_ENABLED = True
# WEBSSO_CHOICES = (
#     ("openid", "Keycloak SSO"),
# )
# WEBSSO_INITIAL_CHOICE = "openid"