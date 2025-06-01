from pydantic import BaseModel


class CreateProfileRequest(BaseModel):
    profile_name: str
    raw_proxy: str
