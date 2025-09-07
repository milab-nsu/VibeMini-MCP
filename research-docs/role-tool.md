# IAM Role Management Tool Research

## Phase 1: Research (API Documentation)

### API Endpoints
- **Get Roles**: `https://api.seliseblocks.com/iam/v1/Resource/GetRoles`
- **Create Role**: `https://api.seliseblocks.com/iam/v1/Resource/CreateRole`

### Headers Required
- `authorization`: Bearer token
- `content-type`: application/json
- `x-blocks-key`: d7e5554c758541db8a18694b64ef423d
- Standard CORS and security headers

## Phase 2: Discovery (Network Requests from UI)

### Get Roles Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetRoles' \
  -H 'accept: application/json' \
  -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","page":0,"pageSize":10,"filter":{"search":""},"sort":{"property":"Name","isDescending":false}}'
```

**Request Payload**:
```json
{
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "page": 0,
  "pageSize": 10,
  "filter": {
    "search": ""
  },
  "sort": {
    "property": "Name",
    "isDescending": false
  }
}
```

**Response**:
```json
{
  "totalCount": 0,
  "data": [],
  "errors": null
}
```

### Create Role Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/CreateRole' \
  -H 'accept: application/json' \
  -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"master","description":"mastering","slug":"master","projectKey":"fcdb6d87-0f9e-42c4-9748-123fea9e088a"}'
```

**Request Payload**:
```json
{
  "name": "master",
  "description": "mastering",
  "slug": "master",
  "projectKey": "fcdb6d87-0f9e-42c4-9748-123fea9e088a"
}
```

**Response**:
```json
{
  "itemId": "47a2e62c-5f9a-4402-8dcf-20ccd38ccc7f",
  "errors": null,
  "isSuccess": true
}
```

## Phase 3: Testing (Curl Commands)

### Test 1: Get Roles (Empty Project)
```bash
# MyTodoApp project - should return empty roles initially
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetRoles' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","page":0,"pageSize":10,"filter":{"search":""},"sort":{"property":"Name","isDescending":false}}'
```

### Test 2: Create Role
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/CreateRole' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"admin","description":"Administrator role","slug":"admin","projectKey":"95E5FD12E64E429295758B2CB1EA29D2"}'
```

### Test 3: Get Roles (After Creation)
```bash
# Should now return the created role
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetRoles' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","page":0,"pageSize":10,"filter":{"search":""},"sort":{"property":"Name","isDescending":false}}'
```

## Phase 4: Implementation

### Tool Functions Required
1. **list_roles**: Get all roles for a project with pagination and filtering
2. **create_role**: Create a new role with name, description, and slug

### Parameters

#### list_roles
- `project_key`: Project key (tenant ID)
- `page`: Page number (default: 0)
- `page_size`: Number of items per page (default: 10)
- `search`: Search filter (default: "")
- `sort_by`: Field to sort by (default: "Name")
- `sort_descending`: Sort order (default: false)

#### create_role
- `name`: Role name
- `description`: Role description
- `slug`: Role slug (URL-friendly identifier)
- `project_key`: Project key (tenant ID)

## Phase 5: Integration

### API Configuration
Add to `API_CONFIG` in `selise_mcp_server.py`:
```python
"IAM_GET_ROLES_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetRoles",
"IAM_CREATE_ROLE_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreateRole",
```

### MCP Tools
- `list_roles`: List all roles for a project
- `create_role`: Create a new role

## Key Findings

1. **Role Structure**:
   - Roles have a name, description, and slug
   - Slug is used as a URL-friendly identifier
   - Each role gets a unique itemId upon creation

2. **Pagination**:
   - Uses page (0-indexed) and pageSize
   - Returns totalCount with data array

3. **Filtering**:
   - Filter object with search field
   - Sort object with property and isDescending

4. **Response Format**:
   - GetRoles: Returns {totalCount, data, errors}
   - CreateRole: Returns {itemId, errors, isSuccess}

## Screenshots Analysis

From the screenshots provided:
1. First screenshot shows empty roles list for MyTodoApp project
2. Second screenshot shows "Add Role" dialog with fields for Name, Slug, and Description
3. Third screenshot shows successfully created "master" role with permissions count of 0