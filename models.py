import re

from pydantic import BaseModel, Field, field_validator



class EmptyProps(BaseModel):
    pass


class EmailProps(BaseModel):  #
    email: str = Field(..., description="email")

    @field_validator("email", mode='after')
    @classmethod
    def validate_email(cls, value):
        email_regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        )
        if not email_regex.match(value):
            raise ValueError("Invalid email format")
        return value
