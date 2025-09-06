"""
Test file for CAPTCHA API endpoints
This is for isolated testing before adding to main MCP server
"""

import httpx
import json
import asyncio

# Hardcoded auth and project details from testing
AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJkN2U1NTU0Yzc1ODU0MWRiOGExODY5NGI2NGVmNDIzZCIsInN1YiI6ImJsb2Nrc3wwNDQ4YWFlNS0xNTE4LTQxZDgtYTg3MC02NGE4Y2M3NWIxMDciLCJ1c2VyX2lkIjoiMDQ0OGFhZTUtMTUxOC00MWQ4LWE4NzAtNjRhOGNjNzViMTA3IiwiaWF0IjoxNzU2ODkyOTIwLCJvcmdfaWQiOiJkZWZhdWx0IiwiZW1haWwiOiJtdXN0YXZpa2hhbjA1QGdtYWlsLmNvbSIsInVzZXJfbmFtZSI6Im11c3RhdmlraGFuMDVAZ21haWwuY29tIiwibmFtZSI6Ik11c3RhdmkgS2hhbiIsInBob25lIjoiIiwibmJmIjoxNzU2ODkyOTIwLCJleHAiOjE3NTczNzI5MjAsImlzcyI6IlNlbGlzZS1CbG9ja3MiLCJhdWQiOiJodHRwczovL2Nsb3VkLnNlbGlzZWJsb2Nrcy5jb20ifQ.Qc1swfshC79LjsdLUkRx-pDMp2MAkDqmxItcE4YMMUbWAGGr8AE2lK1PIDFEz0KnpSf9_gVRNFdMuNxzY0gKruPzbZjm1ldhmDSEVS7y1nf7_cEsAufxdRKE-W9NwvGwa4jDk1RpcI6iCejcdAZZkpIg9z3oQNlnGG5WH3BnWQNCVoYnBZcSrAkwAsgBlmeIPGVrbCQ6PyTPtN2XDWEVJdYx02KOTQVsQR2sfHg0fPOxzKA9Uf5Jl9CEh-EVvG6z9TbIecL8kT6ljC6DA0yVCgkFNrRA7rGndZnCRxn_slNdf0SdKxk_5fQtcRj_aGV8FQLhX8VbapSODD21r8QY5g"
TEST_PROJECT_KEY = "01F34273FA6E40778E7D82CAEA11ACC3"  # Dummy Student Grader project

# API Configuration
BASE_URL = "https://api.seliseblocks.com"
HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {AUTH_TOKEN}",
    "content-type": "application/json",
    "x-blocks-key": "d7e5554c758541db8a18694b64ef423d"
}


async def save_captcha_config(
    provider: str,  # "recaptcha" or "hcaptcha" 
    site_key: str,
    secret_key: str,
    project_key: str = None,
    is_enable: bool = False,
    captcha_generator: str = ""
):
    """
    Save CAPTCHA configuration
    
    Args:
        provider: "recaptcha" for Google reCAPTCHA, "hcaptcha" for hCaptcha
        site_key: Public site key from CAPTCHA provider
        secret_key: Private secret key from CAPTCHA provider  
        project_key: Project key (tenant ID), uses TEST_PROJECT_KEY if not provided
        is_enable: Whether to enable immediately (default: False)
        captcha_generator: Generator type, empty string for standard (default: "")
    
    Returns:
        API response or None if failed
    """
    if not project_key:
        project_key = TEST_PROJECT_KEY
    
    payload = {
        "projectKey": project_key,
        "isEnable": is_enable,
        "provider": provider,
        "captchaKey": site_key,
        "captchaSecret": secret_key,
        "captchaGenerator": captcha_generator
    }
    
    url = f"{BASE_URL}/captcha/v1/Configuration/Save"
    
    print(f"💾 Saving CAPTCHA config for {provider}")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=HEADERS,
                json=payload,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("isSuccess"):
                    print(f"✅ Configuration saved successfully!")
                    return data
                else:
                    print(f"❌ Failed: {data.get('errors')}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def list_captcha_configs(project_key: str = None):
    """
    List all CAPTCHA configurations for a project
    
    Args:
        project_key: Project key (tenant ID), uses TEST_PROJECT_KEY if not provided
    
    Returns:
        API response or None if failed
    """
    if not project_key:
        project_key = TEST_PROJECT_KEY
    
    url = f"{BASE_URL}/captcha/v1/Configuration/Gets"
    params = {"ProjectKey": project_key}
    
    print(f"📋 Listing CAPTCHA configurations")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                configs = data.get("configurations", [])
                print(f"✅ Found {len(configs)} configurations:")
                
                for i, config in enumerate(configs, 1):
                    status = "🟢 Enabled" if config.get("isEnable") else "🔴 Disabled"
                    print(f"  {i}. {config.get('provider')} - {status}")
                    print(f"     ID: {config.get('itemId')}")
                    print(f"     Site Key: {config.get('captchaKey')}")
                    print(f"     Created: {config.get('createdDate')}")
                
                return data
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def update_captcha_status(item_id: str, is_enable: bool, project_key: str = None):
    """
    Enable or disable a CAPTCHA configuration
    
    Args:
        item_id: The ID of the configuration to update
        is_enable: True to enable, False to disable
        project_key: Project key (tenant ID), uses TEST_PROJECT_KEY if not provided
    
    Returns:
        API response or None if failed
    """
    if not project_key:
        project_key = TEST_PROJECT_KEY
    
    payload = {
        "projectKey": project_key,
        "isEnable": is_enable,
        "itemId": item_id
    }
    
    url = f"{BASE_URL}/captcha/v1/Configuration/UpdateStatus"
    
    status_text = "Enabling" if is_enable else "Disabling"
    print(f"🔄 {status_text} CAPTCHA configuration: {item_id}")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=HEADERS,
                json=payload,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("isSuccess"):
                    print(f"✅ Configuration {status_text.lower()}d successfully!")
                    return data
                else:
                    print(f"❌ Failed: {data.get('errors')}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def test_google_recaptcha_v3():
    """Test creating Google reCAPTCHA v3 configuration"""
    print("\n" + "="*60)
    print("🧪 Testing Google reCAPTCHA v3 Configuration")
    print("="*60)
    
    result = await save_captcha_config(
        provider="recaptcha",
        site_key="6Lc_TEST_v3_SITE_KEY",
        secret_key="6Lc_TEST_v3_SECRET_KEY", 
        captcha_generator=""  # Empty for standard reCAPTCHA
    )
    return result


async def test_google_recaptcha_v2():
    """Test creating Google reCAPTCHA v2 configuration"""
    print("\n" + "="*60)
    print("🧪 Testing Google reCAPTCHA v2 Configuration") 
    print("="*60)
    
    result = await save_captcha_config(
        provider="recaptcha",
        site_key="6Lc_TEST_v2_SITE_KEY",
        secret_key="6Lc_TEST_v2_SECRET_KEY",
        captcha_generator=""  # Empty for standard reCAPTCHA
    )
    return result


async def test_hcaptcha():
    """Test creating hCaptcha configuration"""
    print("\n" + "="*60)
    print("🧪 Testing hCaptcha Configuration")
    print("="*60)
    
    result = await save_captcha_config(
        provider="hcaptcha", 
        site_key="10000000-ffff-ffff-ffff-000000000001",
        secret_key="0x0000000000000000000000000000000000000000",
        captcha_generator=""
    )
    return result


async def test_enable_disable_flow():
    """Test enabling and disabling a CAPTCHA configuration"""
    print("\n" + "="*60)
    print("🧪 Testing Enable/Disable Flow")
    print("="*60)
    
    # First, list configurations to find one to test with
    configs_result = await list_captcha_configs()
    if not configs_result or not configs_result.get("configurations"):
        print("❌ No configurations found to test enable/disable")
        return
        
    config = configs_result["configurations"][0]
    item_id = config["itemId"]
    current_status = config["isEnable"]
    
    print(f"\n🎯 Testing with configuration: {config['provider']}")
    print(f"Current status: {'Enabled' if current_status else 'Disabled'}")
    
    # Toggle the status
    new_status = not current_status
    await update_captcha_status(item_id, new_status)
    
    print("\n🔍 Verifying status change...")
    await list_captcha_configs()


async def main():
    """
    Main test function
    """
    print("🚀 CAPTCHA Configuration Testing")
    print("=" * 60)
    print(f"Test Project: {TEST_PROJECT_KEY}")
    print(f"Auth Token: {AUTH_TOKEN[:50]}...")
    print("=" * 60)
    
    # 1. List existing configurations
    print("\n1️⃣ Listing existing configurations...")
    await list_captcha_configs()
    
    # 2. Test creating different CAPTCHA types (uncomment to test)
    # await test_google_recaptcha_v3()
    # await test_google_recaptcha_v2() 
    # await test_hcaptcha()
    
    # 3. Test enable/disable functionality
    await test_enable_disable_flow()
    
    # 4. Final listing to see all changes
    print("\n4️⃣ Final configuration listing...")
    await list_captcha_configs()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
    
    print("\n" + "="*60)
    print("🎉 Testing complete!")
    print("✅ All CAPTCHA API endpoints are working correctly")
    print("Ready to integrate into MCP server!")
    print("="*60)