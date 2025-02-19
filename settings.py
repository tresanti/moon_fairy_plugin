from datetime import date, time
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ValidationError

def validate_threshold(value):
    if value is not None:
        return True

    return False



class FairySettings(BaseModel):
    use_smtp_email: bool = Field(default=False, description="Select if you want to use SMTP email.")
    smtp_server: str = Field(default="", description="Insert the SMTP server.")
    smtp_port: int = Field(default=587, description="Insert the SMTP port.")
    sender_email: str = Field(default="", description="Insert the sender email.")
    sender_password: str = Field(default="", description="Insert the sender password.")
    smtp_tls: bool = Field(default=False, description="Select if you want to use TLS.")

    @field_validator("smtp_server")
    @classmethod
    def check_field_smtp_server(cls, threshold):
        if not validate_threshold(threshold):
            raise ValueError("SMTP server must be between 0 and 1")

    @field_validator('smtp_port')
    @classmethod
    def check_smtp_port_required(cls, threshold):
        if not validate_threshold(threshold):
            raise ValueError('SMTP Port is required!')

    @field_validator('sender_email')
    @classmethod
    def check_sender_email_required(cls, threshold):
        if not validate_threshold(threshold):
            raise ValueError('Sender Email is required!')

    @field_validator('sender_password')
    @classmethod
    def check_sender_password_required(cls, threshold):
        if not validate_threshold(threshold):
            raise ValueError('Sender Password is required!')