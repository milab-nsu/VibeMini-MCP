# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Selise Cloud integration. It provides tools for authentication, project management, schema creation, and repository setup within the Selise Cloud ecosystem.

## Technology Stack

- **Language**: Python 3.8+
- **MCP Framework**: FastMCP
- **HTTP Client**: httpx
- **Dependencies**: httpx>=0.24.0, fastmcp>=0.1.0

## Common Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add to Claude Code as MCP server
claude mcp add selise-cloud python /absolute/path/to/selise_mcp_server.py
```

### Running the Server
```bash
# The server runs as an MCP plugin within Claude Code
python selise_mcp_server.py
```

## Architecture

### Core Components

1. **Global State Management** (`selise_mcp_server.py:12-25`)
   - `auth_state`: Manages authentication tokens, expiration times
   - `app_state`: Tracks application domain, tenant ID, project name

2. **API Configuration** (`selise_mcp_server.py:27-56`)
   - Centralized API endpoints for Selise Cloud services
   - Security headers matching Selise Cloud web interface requirements

3. **Authentication Flow**
   - Token-based authentication with automatic expiration tracking
   - Bearer token injection into API requests via `get_auth_headers()`

### MCP Tools Structure

The server exposes 16 tools through the FastMCP framework:

**Authentication & State**:
- `login`: OAuth token authentication
- `get_auth_status`: Check authentication validity
- `get_global_state`: Retrieve current auth and app state

**Project Management**:
- `get_projects`: List projects and extract application domains
- `create_project`: Create new Selise Cloud projects
- `set_application_domain`: Manually configure domain and tenant

**Schema Operations** (GraphQL):
- `create_schema`: Create new schemas
- `list_schemas`: Search and list schemas
- `get_schema`: Retrieve schema details
- `update_schema_fields`: Modify schema fields
- `finalize_schema`: Commit schema changes

**Repository & CLI**:
- `check_blocks_cli`: Verify Blocks CLI installation
- `install_blocks_cli`: Install via npm
- `create_local_repository`: Generate local Selise repositories

**Configuration**:
- `activate_social_login`: Configure OAuth providers
- `get_authentication_config`: Retrieve auth configuration

### Key Design Patterns

1. **Async/Await Pattern**: All tools use async functions for non-blocking operations
2. **Token Validation**: `is_token_valid()` checks expiration before API calls
3. **Command Execution**: `run_command()` provides async subprocess handling for CLI operations
4. **Consistent Error Handling**: All tools return JSON with status/message structure

## Important Notes

### Schema Naming Conflict
Selise Cloud currently doesn't support duplicate schema names across different projects/accounts. If schema creation fails, use a unique name.

### Authentication Requirements
- Users must have a registered Selise Cloud account
- Tokens expire and require re-authentication
- Project operations require valid application domain and tenant ID

### Security Considerations
- Never commit the API key (`x-blocks-key`) changes
- Access tokens are managed in memory only
- All API requests include required security headers

## Tool Development Process

When adding new services/tools to the MCP server, follow this structured process:

### 1. Research Phase
- Read API documentation from `/docs` folder or Swagger
- Create a research document named `{service}-tool.md` (e.g., `captcha-tool.md`)
- Document available endpoints, parameters, and response structures

### 2. Discovery Phase
- User performs actual actions in Selise Cloud UI
- Capture network tab requests/responses and screenshots
- Add all network details to the research document
- Note any discrepancies between docs and actual API behavior

### 3. Testing Phase
- Test each endpoint with curl commands
- Document working curl commands in the research document
- Verify request/response formats and required headers

### 4. Implementation Phase
- Create `test_{service}.py` with hardcoded auth for isolated testing
- Test each tool function independently
- Verify results appear correctly in Selise Cloud

### 5. Integration Phase
- Only after verification, add tools to `selise_mcp_server.py`
- Add new endpoints to `API_CONFIG`
- Implement tools following existing patterns
- Use existing auth state and error handling

This methodical approach ensures each tool is properly researched, tested, and verified before integration.