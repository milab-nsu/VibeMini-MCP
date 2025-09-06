# CAPTCHA Tool Implementation Research

## Overview
This document tracks the implementation of CAPTCHA services (Google reCAPTCHA and hCaptcha) for the Selise MCP server.

## API Endpoints Available

### Configuration Endpoints
1. **POST /captcha/v1/Configuration/Save** - Save CAPTCHA configuration
   - Parameters: captchaKey, captchaSecret, provider, captchaGenerator, isEnable, projectKey
   - Response: itemId on success

2. **GET /captcha/v1/Configuration/Get** - Get specific configuration
   - Query params: ProviderName, ProjectKey
   - Response: Configuration details

3. **GET /captcha/v1/Configuration/Gets** - Get all configurations
   - Query params: ProjectKey
   - Response: Array of configurations

4. **POST /captcha/v1/Configuration/UpdateStatus** - Enable/disable configuration
   - Parameters: itemId, isEnable, projectKey
   - Response: Success status

### CAPTCHA Operations
1. **POST /captcha/v1/Captcha/Create** - Create CAPTCHA challenge
   - Parameters: configurationName
   - Response: id, captcha token

2. **POST /captcha/v1/Captcha/Submit** - Submit CAPTCHA response
   - Parameters: id, value (user's response)
   - Response: verificationCode

3. **GET /captcha/v1/Captcha/Verify** - Verify CAPTCHA
   - Query params: VerificationCode, ConfigurationName
   - Response: verified status, hostName

## Implementation Plan

### Phase 1: Configuration Setup
We need to create tools for:
1. `save_captcha_config` - Save Google reCAPTCHA or hCaptcha configuration
2. `get_captcha_config` - Retrieve configuration by provider
3. `list_captcha_configs` - List all CAPTCHA configurations
4. `update_captcha_status` - Enable/disable CAPTCHA

### Phase 2: CAPTCHA Operations
Tools for runtime operations:
1. `create_captcha` - Generate CAPTCHA challenge
2. `submit_captcha` - Submit user's CAPTCHA response
3. `verify_captcha` - Verify CAPTCHA solution

## Provider Types
- **Google reCAPTCHA v2** - Challenge-based (I'm not a robot checkbox)
- **Google reCAPTCHA v3** - Score-based (invisible, risk analysis)
- **hCaptcha** - Privacy-focused alternative to reCAPTCHA

## Required Information from User

### For Google reCAPTCHA:
- Site Key (public key)
- Secret Key (private key)
- Type (v2 Challenge or v3 Score-based)
- Domains (where it will be used)

### For hCaptcha:
- Site Key
- Secret Key
- Domains

## Testing Journey

### Test 1: Save Google reCAPTCHA v3 Configuration
```bash
# Will add actual curl command after capturing from network tab
```

### Test 2: Save Google reCAPTCHA v2 Configuration
```bash
# Will add actual curl command after capturing from network tab
```

### Test 3: Save hCaptcha Configuration
```bash
# Will add actual curl command after capturing from network tab
```

## Network Requests Log

### Request 1: Initial Page Load (Component Fetch)
- **URL**: https://cloud.seliseblocks.com/services/captcha
- **Method**: POST
- **Purpose**: Loads the CAPTCHA service component/UI
- **Note**: This is a Next.js app router request for loading the UI component. NOT needed for API operations.

### Request 2: Save CAPTCHA Configuration ✅
- **URL**: https://api.seliseblocks.com/captcha/v1/Configuration/Save
- **Method**: POST
- **Headers**: 
  - authorization: Bearer {token}
  - x-blocks-key: d7e5554c758541db8a18694b64ef423d
  - content-type: application/json
- **Payload**:
```json
{
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "isEnable": false,
  "provider": "recaptcha",
  "captchaKey": "6LdgksArAAAAANkmwwKlu6V2O8xhhx0kJhQZR2j-",
  "captchaSecret": "6LdgksArAAAAADVsfOGH6LW6luMnA_qR368RNo-4",
  "captchaGenerator": ""
}
```
- **Response**:
```json
{
  "itemId": null,
  "errors": null,
  "isSuccess": true
}
```

### Request 3: List CAPTCHA Configurations ✅
- **URL**: https://api.seliseblocks.com/captcha/v1/Configuration/Gets?ProjectKey=95E5FD12E64E429295758B2CB1EA29D2
- **Method**: GET
- **Headers**: 
  - authorization: Bearer {token}
  - x-blocks-key: d7e5554c758541db8a18694b64ef423d
- **Response**:
```json
{
  "configurations": [
    {
      "captchaKey": "6LdgksArAAAAANkmwwKlu6V2O8xhhx0kJhQZR2j-",
      "captchaSecret": "6LdgksArAAAAADVsfOGH6LW6luMnA_qR368RNo-4",
      "provider": "recaptcha",
      "captchaGenerator": "",
      "isEnable": false,
      "itemId": "92770bc7-d7d8-4361-9f31-eddc431f4485",
      "createdDate": "2025-09-06T18:12:32.372Z",
      "lastUpdatedDate": "2025-09-06T18:12:32.372Z",
      "createdBy": "95E5FD12E64E429295758B2CB1EA29D2",
      "language": null,
      "lastUpdatedBy": "95E5FD12E64E429295758B2CB1EA29D2",
      "organizationIds": [],
      "tags": []
    }
  ]
}
```

### Request 4: Enable/Disable CAPTCHA Configuration ✅
- **URL**: https://api.seliseblocks.com/captcha/v1/Configuration/UpdateStatus
- **Method**: POST
- **Headers**: 
  - authorization: Bearer {token}
  - x-blocks-key: d7e5554c758541db8a18694b64ef423d
  - content-type: application/json
- **Payload**:
```json
{
  "projectKey": "95E5FD12E64E429295758B2CB1EA29D2",
  "isEnable": true,
  "itemId": "92770bc7-d7d8-4361-9f31-eddc431f4485"
}
```
- **Response**:
```json
{
  "itemId": null,
  "errors": null,
  "isSuccess": true
}
```

### Request 5: Verify Updated Status ✅
- After enabling, the Gets endpoint shows `"isEnable": true` in the configuration 

## Key Findings from Network Analysis

1. **Provider Value**: Uses `"recaptcha"` not `"google"` for Google reCAPTCHA
2. **captchaGenerator**: Empty string `""` for standard Google reCAPTCHA (not "v2" or "v3")
3. **isEnable**: Defaults to `false` when creating
4. **itemId in response**: Returns `null` on save but configuration gets created with actual ID
5. **Project Key**: Uses tenant ID format like `95E5FD12E64E429295758B2CB1EA29D2`

## Differences Between Documentation and Actual API

| Field | Documentation | Actual API |
|-------|--------------|------------|
| provider | Not specified | "recaptcha" for Google |
| captchaGenerator | Not specified | Empty string "" |
| Response itemId | Should return ID | Returns null (but config is created) |
| configurationName | In docs | Not used in actual payload |

## Notes and Observations
- Domain validation: Must be hostname only, no protocol/path/port  
- The UI shows "Label" field but API doesn't use it in the payload
- Configuration is created successfully even though itemId returns null
- The Gets endpoint returns the full configuration with the actual itemId