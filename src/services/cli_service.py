import json
from utils import misc


async def check_blocks_cli() -> str:
    """Check if Blocks CLI is installed and available."""
    result = await misc.run_command("blocks --version")

    if result["success"]:
        return json.dumps({
            "status": "success",
            "message": "Blocks CLI is installed and available",
            "version": result["stdout"]
        }, indent=2)
    else:
        return json.dumps({
            "status": "not_installed",
            "message": "Blocks CLI is not installed",
            "error": result["stderr"]
        }, indent=2)


async def install_blocks_cli() -> str:
    """Install Blocks CLI using npm."""
    result = await misc.run_command("npm install -g @seliseblocks/cli")

    if result["success"]:
        # Verify installation
        verify_result = await misc.run_command("blocks --version")

        return json.dumps({
            "status": "success",
            "message": "Blocks CLI installed successfully",
            "installation_output": result["stdout"],
            "version": verify_result["stdout"] if verify_result["success"] else "Unknown"
        }, indent=2)
    else:
        return json.dumps({
            "status": "error",
            "message": "Failed to install Blocks CLI",
            "error": result["stderr"],
            "output": result["stdout"]
        }, indent=2)
