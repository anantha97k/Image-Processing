import time
from functools import wraps

import redis
from fastapi import HTTPException, Request

ip_addr = redis.Redis()


def custom_limiter(func):

    @wraps(func)
    async def limiter_wrapper(request: Request, *args, **kwargs):
        current_time = time.time()
        max_request = 2
        window_seconds = 60

        key = f"ip:{request.client.host}"  # type: ignore

        if ip_addr.llen(key) >= max_request:  # type: ignore
            retry_after = window_seconds - (
                current_time - float(ip_addr.lindex(key, 0))  # type: ignore
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Too Many Requests",
                    "message": "You have reached your request limit. "
                    "Please try again later or contact support.",
                    "retryAfter": round(retry_after, 0),
                },
            )

        ip_addr.lpush(key, current_time)
        if ip_addr.llen(key) == 1:
            ip_addr.expire(key, window_seconds)

        return await func(request, *args, **kwargs)

    return limiter_wrapper
