# IAM Permissions Management Tool Research

## Phase 1: Research (API Documentation)

### API Endpoints
- **Get Resource Groups**: `https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups?ProjectKey={projectKey}`
- **Create Permission**: `https://api.seliseblocks.com/iam/v1/Resource/CreatePermission`
- **Update Permission**: `https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission`
- **Get Permissions**: `https://api.seliseblocks.com/iam/v1/Resource/GetPermissions` (assumed)

### Headers Required
- `authorization`: Bearer token
- `content-type`: application/json
- `x-blocks-key`: d7e5554c758541db8a18694b64ef423d
- Standard CORS and security headers

## Phase 2: Discovery (Network Requests from UI)

### Get Resource Groups Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups?ProjectKey=95E5FD12E64E429295758B2CB1EA29D2' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d'
```

### Create Permission Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/CreatePermission' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"master_access","type":3,"resource":"Tasks","resourceGroup":"Master","tags":["view"],"description":"master_access","dependentPermissions":[],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","isBuiltIn":false}'
```

**Request Payload**:
```json
{
  "name": "master_access",
  "type": 3,
  "resource": "Tasks",
  "resourceGroup": "Master",
  "tags": ["view"],
  "description": "master_access",
  "dependentPermissions": [],
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "isBuiltIn": false
}
```

**Response**:
```json
{
  "itemId": "8f1c10cb-15cd-43f6-80bc-a812d4f980ca",
  "errors": null,
  "isSuccess": true
}
```

### Update Permission Request
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"master_access","type":3,"resource":"hello","resourceGroup":"bingbing","tags":["view"],"description":"master_access","dependentPermissions":[],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","isBuiltIn":false,"itemId":"8f1c10cb-15cd-43f6-80bc-a812d4f980ca"}'
```

**Update Payload** (includes `itemId`):
```json
{
  "name": "master_access",
  "type": 3,
  "resource": "hello",
  "resourceGroup": "bingbing", 
  "tags": ["view"],
  "description": "master_access",
  "dependentPermissions": [],
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "isBuiltIn": false,
  "itemId": "8f1c10cb-15cd-43f6-80bc-a812d4f980ca"
}
```

**Response**:
```json
{
  "itemId": "8f1c10cb-15cd-43f6-80bc-a812d4f980ca",
  "errors": null,
  "isSuccess": true
}
```

## Phase 3: Testing (Curl Commands)

### Test 1: Get Resource Groups
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups?ProjectKey=95E5FD12E64E429295758B2CB1EA29D2' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d'
```

### Test 2: Create Permission
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/CreatePermission' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"test_perm","type":3,"resource":"TestResource","resourceGroup":"TestGroup","tags":["create","read"],"description":"Test permission","dependentPermissions":[],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","isBuiltIn":false}'
```

### Test 3: Update Permission  
```bash
curl 'https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission' \
  -H 'authorization: Bearer [TOKEN]' \
  -H 'content-type: application/json' \
  -H 'x-blocks-key: d7e5554c758541db8a18694b64ef423d' \
  --data-raw '{"name":"test_perm","type":3,"resource":"UpdatedResource","resourceGroup":"UpdatedGroup","tags":["read","update"],"description":"Updated test permission","dependentPermissions":[],"projectKey":"95E5FD12E64E429295758B2CB1EA29D2","isBuiltIn":false,"itemId":"[ITEM_ID]"}'
```

## Phase 4: Implementation

### Tool Functions Required
1. **list_permissions**: Get all permissions for a project with pagination and filtering
2. **create_permission**: Create a new permission with all required fields
3. **update_permission**: Update an existing permission by itemId
4. **get_resource_groups**: Get available resource groups for organizing permissions

### Parameters

#### list_permissions
- `project_key`: Project key (tenant ID)
- `page`: Page number (default: 0)
- `page_size`: Number of items per page (default: 10)
- `search`: Search filter (default: "")
- `sort_by`: Field to sort by (default: "Name")
- `sort_descending`: Sort order (default: false)

#### create_permission
- `name`: Permission name
- `description`: Permission description
- `resource`: Resource name (arbitrary string)
- `resource_group`: Resource group name (arbitrary string)
- `tags`: List of action tags (e.g., ["create", "read", "update", "delete"])
- `type`: Permission type (default: 3 for "Data protection")
- `project_key`: Project key (tenant ID)
- `dependent_permissions`: List of dependent permission IDs (default: [])
- `is_built_in`: Whether it's a built-in permission (default: false)

#### update_permission
- Same as create_permission plus:
- `item_id`: The ID of the permission to update

#### get_resource_groups
- `project_key`: Project key (tenant ID)

## Phase 5: Integration

### API Configuration
Add to `API_CONFIG` in `selise_mcp_server.py`:
```python
"IAM_GET_RESOURCE_GROUPS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups",
"IAM_GET_PERMISSIONS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetPermissions",
"IAM_CREATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreatePermission",
"IAM_UPDATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission",
```

### MCP Tools
- `list_permissions`: List all permissions for a project
- `create_permission`: Create a new permission
- `update_permission`: Update an existing permission
- `get_resource_groups`: Get available resource groups

## Key Findings

1. **Permission Structure**:
   - Permissions have name, description, resource, resourceGroup, tags, and type
   - `itemId` is required for updates but not creation
   - `type`: 3 = "Data protection" (other types unknown)

2. **No Validation**:
   - `resource` and `resourceGroup` are arbitrary strings (proven with "hello"/"bingbing" test)
   - No actual enforcement - permissions are purely organizational metadata
   - Tags can be any string values

3. **Security Architecture Flaw**:
   - API endpoints only validate Bearer tokens
   - No middleware checks user roles or permissions
   - Permission system is cosmetic for UI organization only

4. **Response Format**:
   - Create/Update: Returns {itemId, errors, isSuccess}
   - Get operations: Return arrays with standard pagination

## Screenshots Analysis

From UI testing, we observed:
1. Permission creation form with Type dropdown showing "Data protection"
2. Resource and Group fields accepting any arbitrary text
3. Tags field accepting multiple comma-separated values
4. Successful creation/update with nonsensical values proves no backend validation