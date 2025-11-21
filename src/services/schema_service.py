# """Data Gateway Service for handling schema operations."""

# from src.models import (
#     Config,
#     CreateSchemaRequest,
#     UpdateSchemaRequest,
#     DataGatewayResponse,
# )
# from utils.logger import get_logger
# import src.utils.http_client as http_client
# from src.validators import (
#     validate_create_schema_request,
#     validate_update_schema_request,
# )
# from . import auth_service

# logger = get_logger(__name__)


# def _get_base_url() -> str:
#     """Get the base URL for API requests."""
#     config = Config()
#     return f"{config.api_base_url}/graphql/v1"


# async def create_schema(request: CreateSchemaRequest) -> DataGatewayResponse:
#     """Create a new schema via POST to /schemas/define endpoint."""
#     logger.info("Starting schema creation request")

#     try:
#         # Validate the request first
#         validation_response = validate_create_schema_request(request)
#         if not validation_response.success:
#             return DataGatewayResponse(success=False, errors=validation_response.errors)

#         base_url = _get_base_url()
#         url = f"{base_url}/schemas/define"
#         logger.info(f"Schema creation URL: {url}")

#         config = Config()
#         access_token = await auth_service.get_access_token()

#         # Prepare request data
#         request_data = (
#             request.model_dump() if hasattr(request, "model_dump") else request.__dict__
#         )
#         logger.info(f"Schema creation request data: {request_data}")

#         logger.info("Making POST request to create schema")
#         response_data = await http_client.post(
#             url=url,
#             json=request_data,
#             blocks_key=config.blocks_key,
#             access_token=access_token,
#         )

#         logger.info(f"Schema creation response: {response_data}")
#         return DataGatewayResponse(**response_data)

#     except ValueError as e:
#         logger.error(f"Validation error during schema creation: {e}")
#         raise
#     except Exception:
#         logger.error("Unexpected error during schema creation", exc_info=True)
#         raise


# async def update_schema(request: UpdateSchemaRequest) -> DataGatewayResponse:
#     """Update an existing schema via PUT to /schemas/define endpoint."""
#     logger.info("Starting schema update request")

#     try:
#         # Validate the request first
#         validation_response = validate_update_schema_request(request)
#         if not validation_response.success:
#             return DataGatewayResponse(success=False, errors=validation_response.errors)

#         base_url = _get_base_url()
#         url = f"{base_url}/schemas/define"
#         logger.info(f"Schema update URL: {url}")

#         config = Config()
#         access_token = await auth_service.get_access_token()

#         # Prepare request data
#         request_data = (
#             request.model_dump() if hasattr(request, "model_dump") else request.__dict__
#         )
#         logger.info(f"Schema update request data: {request_data}")

#         logger.info("Making PUT request to update schema")
#         response_data = await http_client.put(
#             url=url,
#             json=request_data,
#             blocks_key=config.blocks_key,
#             access_token=access_token,
#         )

#         logger.info("Schema updated successfully")
#         logger.info(f"Schema update response: {response_data}")
#         return DataGatewayResponse(**response_data)

#     except ValueError as e:
#         logger.error(f"Validation error during schema update: {e}")
#         raise
#     except Exception:
#         logger.error("Unexpected error during schema update", exc_info=True)
#         raise
