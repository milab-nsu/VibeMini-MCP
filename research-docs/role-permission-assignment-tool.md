# IAM Role-Permission Assignment Tool Research

## Phase 1: Research (API Documentation)

### API Endpoints
- **Set Role Permissions**: `https://api.seliseblocks.com/iam/v1/Resource/SetRoles`
- **Get Permissions by Role**: `https://api.seliseblocks.com/iam/v1/Resource/GetPermissions` (with roles filter)

### Headers Required
- `authorization`: Bearer token
- `content-type`: application/json
- `x-blocks-key`: d7e5554c758541db8a18694b64ef423d
- Standard CORS and security headers

## Phase 2: Discovery (Network Requests from UI)

### Set Role Permissions Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/SetRoles' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"addPermissions":["535ec2ca-3b5e-4a6f-8a39-92430edca417"],"removePermissions":[],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","slug":"moderator"}'
```

**Request Payload**:
```json
{
  "addPermissions": ["535ec2ca-3b5e-4a6f-8a39-92430edca417"],
  "removePermissions": [],
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "slug": "moderator"
}
```

### Get Permissions by Role Request  
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetPermissions' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"page":0,"pageSize":10,"roles":["moderator"],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","filter":{"search":"","isBuiltIn":""}}'
```

**Request Payload**:
```json
{
  "page": 0,
  "pageSize": 10,
  "roles": ["moderator"],
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "filter": {
    "search": "",
    "isBuiltIn": ""
  }
}
```

**Response**:
```json
{
  "totalCount": 1,
  "data": [
    {
      "roles": ["moderator"],
      "name": "test_perm",
      "type": 3,
      "description": "Test permission for curl validation",
      "resource": "testresource",
      "resourceGroup": "TestGroup",
      "isBuiltIn": false,
      "isArchived": false,
      "dependentPermissions": [],
      "itemId": "535ec2ca-3b5e-4a6f-8a39-92430edca417",
      "createdDate": "2025-09-06T23:58:35.234Z",
      "lastUpdatedDate": "2025-09-06T23:58:35.234Z",
      "createdBy": "0448aae5-1518-41d8-a870-64a8cc75b107",
      "language": null,
      "lastUpdatedBy": "0448aae5-1518-41d8-a870-64a8cc75b107",
      "organizationIds": [],
      "tags": ["create", "read"]
    }
  ],
  "errors": null
}
```

## Phase 3: Testing (Curl Commands)

### Test 1: Assign Permission to Role
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/SetRoles' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"addPermissions":["PERMISSION_ID"],"removePermissions":[],"projectKey":"PROJECT_KEY","slug":"ROLE_SLUG"}'
```

### Test 2: Remove Permission from Role
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/SetRoles' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"addPermissions":[],"removePermissions":["PERMISSION_ID"],"projectKey":"PROJECT_KEY","slug":"ROLE_SLUG"}'
```

### Test 3: Get Role Permissions
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetPermissions' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"page":0,"pageSize":10,"roles":["ROLE_SLUG"],"projectKey":"PROJECT_KEY","filter":{"search":"","isBuiltIn":""}}'
```

## Phase 4: Implementation

### Tool Functions Required
1. **set_role_permissions**: Assign or remove permissions from a role
2. **get_role_permissions**: Get all permissions assigned to specific role(s)

### Parameters

#### set_role_permissions
- `role_slug`: Role slug identifier
- `add_permissions`: List of permission IDs to add to the role
- `remove_permissions`: List of permission IDs to remove from the role
- `project_key`: Project key (tenant ID)

#### get_role_permissions  
- `role_slugs`: List of role slugs to filter by
- `project_key`: Project key (tenant ID)
- `page`: Page number (default: 0)
- `page_size`: Number of items per page (default: 10)
- `search`: Search filter (default: "")
- `is_built_in`: Filter by built-in status (default: "")

## Phase 5: Integration

### API Configuration
Add to `API_CONFIG` in `selise_mcp_server.py`:
```python
"IAM_SET_ROLES_URL": "https://api.seliseblocks.com/iam/v1/Resource/SetRoles",
# GetPermissions already exists, just extend functionality
```

### MCP Tools
- `set_role_permissions`: Assign/remove permissions to/from roles
- `get_role_permissions`: Get permissions assigned to specific roles

## Key Findings

1. **Role-Permission Association**:
   - Uses role `slug` identifier, not role `itemId`
   - Can add multiple permissions or remove multiple permissions in single request
   - Same GetPermissions endpoint supports role filtering

2. **Payload Structure**:
   - `addPermissions`: Array of permission itemIds to assign
   - `removePermissions`: Array of permission itemIds to unassign
   - Both arrays can be used simultaneously in one request

3. **Response Behavior**:
   - SetRoles endpoint likely returns success/failure response
   - GetPermissions with roles filter returns permissions with `roles` array populated
   - Shows which roles each permission is assigned to

4. **UI Integration**:
   - This enables full role-based access control UI
   - Users can assign permissions to roles dynamically
   - Roles filter in GetPermissions allows viewing role-specific permissions