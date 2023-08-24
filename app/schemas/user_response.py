from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from .vacancy_response import DataResponse


class BaseUserResponse(BaseModel):
    id: UUID = Field(description="ID response.")
    created_on: Optional[datetime] = Field(description="Create datetime of response.")
    data_response: List[DataResponse] = Field(default_factory=list, description="JSON field with information about "
                                                                                "response. Empty value for any key is "
                                                                                "empty string, like this: \"\"")
    vacancy_id: Optional[UUID] = Field(description="ID vacancy. Required.")
    gp_user_id: Optional[UUID] = Field(description="Group of companies  ID user. Empty value: null. "
                                                   "The gp_user_id field or the email and phone fields "
                                                   "must be filled in field of data_response")
    name: Optional[str] = Field(description="Name of vacancy.")
    company_name: Optional[str] = Field(description="Name of company employee.")

    class Config:
        orm_mode = True


class UserResponse(BaseUserResponse):
    pass
