# Selise Cloud MCP Server

A Model Context Protocol (MCP) server for setting up and developing projects in Selise Cloud. This server provides tools for authentication, project management, schema creation, and repository setup within the Selise Cloud ecosystem, designed to be used by AI agents to streamline development workflows.

## Features

- **Authentication**: Login with username/password and manage access tokens
- **Project Management**: Create projects, list existing projects, and manage project configurations
- **Schema Management**: Create, list, update, and manage GraphQL schemas
- **Repository Creation**: Create local Selise repositories using the Blocks CLI
- **Authentication Configuration**: Activate social login and manage authentication settings
- **Global State Management**: Track authentication status and application domains

## Setup

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Blocks CLI installation)
- Claude Code or another MCP-compatible client

### Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add the MCP server to Claude Code**:
   - Open a folder containing the server files in Claude Code
   - Run the following command to add the MCP server:
   ```bash
   claude mcp add selise-cloud python /absolute/path/to/selise_mcp_server.py
   ```

   Replace `/absolute/path/to/selise_mcp_server.py` with the actual path to your server file.

## Available Tools

### Authentication
- `login(username, password)` - Authenticate with Selise Cloud API
- `get_auth_status()` - Check current authentication status
- `get_global_state()` - Get current global state including auth and app state

### Project Management
- `get_projects(tenant_group_id, page, page_size)` - List projects and extract application domains
- `create_project(project_name, repo_name, repo_link, repo_id, is_production)` - Create a new project in Selise Cloud
- `set_application_domain(domain, tenant_id, project_name)` - Manually set application domain and tenant ID

### Schema Management
- `create_schema(schema_name, project_key)` - Create a new GraphQL schema
- `list_schemas(project_key, keyword, page_size, page_number, sort_descending, sort_by)` - List existing schemas
- `get_schema(schema_id, project_key)` - Get schema details by ID
- `update_schema_fields(schema_id, fields, project_key)` - Update schema fields
- `finalize_schema(schema_id, project_key)` - Finalize schema changes

### Repository & CLI Management
- `check_blocks_cli()` - Check if Blocks CLI is installed
- `install_blocks_cli()` - Install Blocks CLI using npm
- `create_local_repository(repository_name, template, use_cli)` - Create a local Selise repository

### Authentication Configuration
- `activate_social_login(item_id, project_key, ...)` - Activate social login for the project
- `get_authentication_config(project_key)` - Get current authentication configuration

## Usage Examples

### Basic Authentication
```python
# Login to Selise Cloud
await login("your-email@example.com", "your-password")

# Check authentication status
await get_auth_status()
```

### Project Setup
```python
# Get list of projects
await get_projects()

# Create a new project
await create_project(
    project_name="my-new-project",
    repo_name="username/my-repo",
    repo_link="https://github.com/username/my-repo.git",
    repo_id="123456789"
)
```

### Schema Management
```python
# Create a new schema
await create_schema("User")

# List all schemas
await list_schemas()

# Get schema by ID
await get_schema("schema-id-here")
```

### Local Repository Creation
```python
# Check if Blocks CLI is installed
await check_blocks_cli()

# Install Blocks CLI if needed
await install_blocks_cli()

# Create a local repository
await create_local_repository("my-app", "web", use_cli=True)
```

## Configuration

The server maintains global state for:
- **Authentication**: Access tokens, refresh tokens, and expiration times
- **Application State**: Current application domain, tenant ID, and project name

This state is automatically managed and updated as you use the various tools.

## Error Handling

All tools return JSON responses with:
- `status`: "success" or "error"
- `message`: Descriptive message about the result
- Additional data specific to each tool

## Security Notes

- Access tokens are automatically managed and validated
- Tokens expire and need to be refreshed by re-authenticating
- The server includes security headers matching the Selise Cloud web interface
- Never commit credentials or tokens to version control

## Troubleshooting

### Authentication Issues
- You need to register an account in Selise Cloud first. 

### CLI Issues
- Ensure Node.js and npm are installed
- Check if the Blocks CLI installation was successful
- Verify global npm permissions

### Schema/Project Issues
- Selise cloud doesn't support the same schema names (to be fixed), even for different projects & accounts. If schema creation fails, try a different name. The agent should tell you when it fails due to naming conflicts.

## API Endpoints

The server communicates with the following Selise Cloud API endpoints:
- Authentication: `https://api.seliseblocks.com/authentication/v1/OAuth/Token`
- Projects: `https://api.seliseblocks.com/identifier/v1/Project/*`
- GraphQL Schemas: `https://api.seliseblocks.com/graphql/v1/schemas/*`
- Configuration: `https://api.seliseblocks.com/authentication/v1/Configuration/*`