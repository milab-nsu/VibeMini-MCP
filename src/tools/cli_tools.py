from server import server as mcp
from services import cli_service


@mcp.tool()
async def check_blocks_cli() -> str:
    """
    Check if Blocks CLI is installed and available.

    Returns:
        JSON string with CLI availability status
    """
    return await cli_service.check_blocks_cli()


@mcp.tool()
async def install_blocks_cli() -> str:
    """
    Install Blocks CLI using npm.

    Returns:
        JSON string with installation result
    """
    return await cli_service.install_blocks_cli()
