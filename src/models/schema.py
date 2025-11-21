"""Data Gateway Models"""

from typing import Any
from pydantic import BaseModel, Field


class SchemaField(BaseModel):
    """Represents a field in a schema."""

    Name: str = Field(..., description="The name of the field")
    Type: str = Field(..., description="The type of the field")
    IsArray: bool = Field(default=True, description="Whether the field is array")


class CreateSchemaRequest(BaseModel):
    """Request model for creating a schema."""

    CollectionName: str = Field(..., description="The name of the collection")
    SchemaName: str = Field(..., description="The name of the schema")
    ProjectKey: str = Field(..., description="The key of the project")
    SchemaType: int = Field(default=1, description="The type of the schema")
    Fields: list[SchemaField] = Field(..., description="The fields of the schema")


class UpdateSchemaRequest(CreateSchemaRequest):
    """Request model for updating a schema."""

    ItemId: str = Field(..., description="The ID of the schema to update")


class DataGatewayResponse(BaseModel):
    """Response model for data gateway operations."""

    isSuccess: bool
    httpStatusCode: int | None
    data: Any | None = Field(
        default=None,
        description="List of created schema items",
    )
    errors: list[Any] | None = Field(
        default=None,
        description="List of errors that occurred during the request",
    )
    message: str | None = Field(
        default=None,
        description="A message providing additional information about the result",
    )
