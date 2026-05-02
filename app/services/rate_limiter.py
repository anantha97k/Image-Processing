import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import Request, Response
from fastapi.exceptions import HTTPException


# 1. Token Management
class TokenBucket:
    """
    Token Bucket Algorithm

    capacity
    refill rate : 4 per 1
    refill interval
    request/token
    """

    def __init__(
        self, capacity: int = 5, refill_interval: float = 1, refill_amount: int = 1
    ) -> None:
        self.capacity = capacity
        self.refill_interval = refill_interval
        self.refill_amount = refill_amount

        self.tokens = capacity
        self.max_retry_attempts = 3
        self.refill_task: Optional[asyncio.Task] = None
        self.pending_tasks: Dict[str, asyncio.Task] = {}

    def init(self):
        if self.refill_task is None:
            self.refill_task = asyncio.create_task(self._refill_tokens())

    async def _refill_tokens(self):
        try:
            while True:
                await asyncio.sleep(self.refill_interval)
                self.tokens = min(self.tokens + self.refill_amount, self.capacity)
        except asyncio.CancelledError:
            pass

    def consume_token(self) -> bool:
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False

    @asynccontextmanager
    async def middleware(self, request: Request, response: Response):
        request_id = self._generate_request_id(request)
        print(request_id)

        try:
            if self.consume_token():
                response.headers["X-RateLimit-Remaining"] = str(self.tokens)
                yield
            else:
                await self.retry_with_backoff(request, response, request_id)
                yield
        finally:
            if request_id in self.pending_tasks:
                task = self.pending_tasks.pop(request_id)
                if not task.done():
                    task.cancel()

    async def retry_with_backoff(
        self, request: Request, response: Response, request_id: str, attempt: int = 1
    ):

        delay = min(2**attempt * 0.1, 2)

        async def retry_callback():
            try:
                self.pending_tasks.pop(request_id, None)
                await asyncio.sleep(delay)

                if self.consume_token():
                    response.headers["X-RateLimit-Remaining"] = str(self.tokens)
                    response.headers["X-RateLimit-Retry-Count"] = str(attempt)
                    return
                elif attempt < self.max_retry_attempts:
                    await self.retry_with_backoff(
                        request, response, request_id, attempt + 1
                    )
                else:
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Too Many Requests",
                            "message": "Rate limit exceeded. Try again later.",
                        },
                    )
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(retry_callback())
        await task

    def _generate_request_id(self, request: Request) -> str:
        """Generate a unique request ID"""
        client_ip = request.client.host if request.client else "unknown"
        return f"{client_ip}:{int(time.time() * 1000)}:{uuid.uuid4().hex[:7]}"

    async def shutdown(self):
        """Clean up resources when shutting down"""
        if self.refill_task:
            self.refill_task.cancel()
            try:
                await self.refill_task
            except asyncio.CancelledError:
                pass
            self.refill_task = None

        # Clean up any pending tasks
        for task in list(self.pending_tasks.values()):
            task.cancel()

        # Wait for tasks to complete cancellation
        if self.pending_tasks:
            await asyncio.gather(*self.pending_tasks.values(), return_exceptions=True)

        self.pending_tasks.clear()
