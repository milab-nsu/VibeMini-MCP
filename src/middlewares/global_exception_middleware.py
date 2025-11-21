from utils.logger import get_logger
from fastmcp.server.middleware import Middleware, MiddlewareContext


class GlobalExceptionMiddleware(Middleware):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_counts = {}

    async def on_message(self, context: MiddlewareContext, call_next):
        try:
            return await call_next(context)
        except Exception as error:
            # Log the error and track statistics
            error_key = f"{type(error).__name__}:{context.method}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

            self.logger.error(
                f"Error in {context.method}: {type(error).__name__}: {error}"
            )
            raise
