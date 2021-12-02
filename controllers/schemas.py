from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, TypeVar, Generic
from pydantic import BaseModel
from pydantic.generics import GenericModel
from enum import Enum

T = TypeVar('T')


class WebResponse(GenericModel, Generic[T]):
    code: int
    message: Optional[str] = ""
    data: Optional[T]


class UserType(str,Enum):
    admin = "超級管理員"
    user = "普通用戶"
    audit = "审计员"


class Menu(BaseModel):
    name: str
    uri: str

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None
    age: float = Field(..., gt=0, description="The age must be greater than zero")
    sex: float = Field(..., gt=0, description="The sex must be greater than zero")

class UserOut(UserIn):
    menus: Optional[List[Menu]]

class AccessToken(BaseModel):
    token:str

