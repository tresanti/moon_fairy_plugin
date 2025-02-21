import re
from pydantic import BaseModel, Field, field_validator, model_validator


def validate_threshold(value):
    if value is None or value == "":
        return False
    return True

def is_valid_email(email):
    # Pattern per la validazione email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


class FairySettings(BaseModel):
    use_smtp_email: bool = Field(default=False, description="Select if you want to use SMTP email.")
    smtp_server: str = Field(default="", description="Insert the SMTP server.")
    smtp_port: int = Field(default=587, description="Insert the SMTP port.")
    sender_email: str = Field(default="", description="Insert the sender email.")
    sender_password: str = Field(default="", description="Insert the sender password.")
    smtp_tls: bool = Field(default=False, description="Select if you want to use TLS.")

    @model_validator(mode='before')
    def reset_fields_if_smtp_disabled(cls, values):
        if not values.get('use_smtp_email', False):
            values['smtp_server'] = ""
            values['smtp_port'] = 587
            values['sender_email'] = ""
            values['sender_password'] = ""
            values['smtp_tls'] = False
        return values

    @model_validator(mode='after')
    def validate_smtp_settings(self) -> 'FairySettings':
        if self.use_smtp_email:
            if not validate_threshold(self.smtp_server):
                raise ValueError("SMTP server is required when SMTP email is enabled")

            if not validate_threshold(str(self.smtp_port)):
                raise ValueError("SMTP Port is required when SMTP email is enabled")

            if not validate_threshold(self.sender_email):
                raise ValueError("Sender Email is required when SMTP email is enabled")

            if not is_valid_email(self.sender_email):
                raise ValueError("Invalid Sender Email format")

            if not validate_threshold(self.sender_password):
                raise ValueError("Sender Password is required when SMTP email is enabled")

        else:
            self.smtp_server = ""
            self.smtp_port = 587
            self.sender_email = ""
            self.sender_password = ""
            self.smtp_tls = False

        return self