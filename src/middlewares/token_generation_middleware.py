from services import auth_service
from utils.misc import auth_state
from utils.logger import get_logger
from fastmcp.server.middleware import Middleware, MiddlewareContext


class TokenGenerationMiddleware(Middleware):
    def __init__(self):
        self.logger = get_logger(__name__)

    async def on_call_tool(self, ctx: MiddlewareContext, call_next):
        auth = await self.get_access_token(ctx)
        auth_state.update(auth)
        return await call_next(ctx)

    async def get_access_token(self, ctx: MiddlewareContext) -> str:
        """
        Authenticate with Selise Blocks API and retrieve access tokens.

        Args:
            username: Email address for login
            password: Password for login

        Returns:
            Access token as a string
        """
        request = ctx.fastmcp_context.get_http_request()
        username = request.headers.get("x-blocks-user", "")
        password = request.headers.get("x-blocks-secret", "")
        self.logger.info(f"Authenticating user: {username} with password: {password}")
        auth_response = await auth_service.get_authentication_tokens(username, password)

        self.logger.info(f"auth_response: {auth_response}")

        return auth_response
