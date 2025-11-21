"""Main entry point for the Selise Blocks MCP Server."""

import sys
import os

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

from tools import *
from prompts import *
from resources import *
from server import server
from utils.logger import get_logger


def main():
    """Run the MCP server."""
    logger = get_logger(__name__)

    logger.info("Starting Selise Blocks MCP Server with HTTP transport on port 8000...")

    try:
        # Import the server instance with registered tools
        server.run(transport="http", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Selise Blocks MCP Server shutdown completed")
        sys.exit(0)
    except Exception:
        logger.error("Failed to start Selise Blocks MCP Server", exc_info=True)
        raise


if __name__ == "__main__":
    main()
