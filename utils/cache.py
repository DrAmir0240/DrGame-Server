from django.core.cache import cache


# Cache key constants
CACHE_KEYS = {
    "otp": "otp:{phone}",
    "otp_attempts": "otp_attempts:{phone}",
    "product_list": "store:products:{hash}",
    "category_list": "store:categories",
    "customer_profile": "customer:{id}:profile",
    "wallet_balance": "wallet:{customer_id}:balance",
}


def get_cached_or_set(key, get_data_func, timeout=300, **kwargs):
    cache_key = key.format(**kwargs)
    data = cache.get(cache_key)
    if data is not None:
        return data
    data = get_data_func()
    cache.set(cache_key, data, timeout)
    return data


def invalidate_cache(key, **kwargs):
    cache_key = key.format(**kwargs)
    cache.delete(cache_key)
