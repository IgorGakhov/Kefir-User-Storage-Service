from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator
import phonenumbers


class UserDataValidateMixin:
    @validator('phone')
    def validate_phone(cls, value):
        exc = ValueError('Неверный номер телефона')
        try:
            parsed_phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise exc
            return value
        except phonenumbers.phonenumberutil.NumberParseException:
            raise exc

    @validator('birthday')
    def validate_birthday(cls, value):
        today = date.today()
        if value > today:
            raise ValueError('День рождения не может быть в будущем')
        return value


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


class CurrentUserResponseModel(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = ...
    email: EmailStr
    phone: Optional[str] = ...
    birthday: Optional[date] = ...
    is_admin: bool


class UpdateUserModel(UserDataValidateMixin, BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None


class UpdateUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: Optional[str] = ...
    email: EmailStr
    phone: Optional[str] = ...
    birthday: Optional[date] = ...


class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr


class UsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel


class UsersListResponseModel(BaseModel):
    data: List[UsersListElementModel]
    meta: UsersListMetaDataModel


class CitiesHintModel(BaseModel):
    id: int
    name: str


class PrivateCreateUserModel(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: bool
    password: str


class PrivateDetailUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: Optional[str] = ...
    email: EmailStr
    phone: Optional[str] = ...
    birthday: Optional[date] = ...
    city: Optional[int] = ...
    additional_info: Optional[str] = ...
    is_admin: bool


class PrivateUpdateUserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: EmailStr = None
    phone: Optional[str] = None
    birthday: date = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: bool = None


class PrivateUsersListHintMetaModel(BaseModel):
    city: List[CitiesHintModel]


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class PrivateUsersListResponseModel(BaseModel):
    data: List[UsersListElementModel]
    meta: PrivateUsersListMetaDataModel
