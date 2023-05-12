import re
from datetime import date
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship, validates
from passlib import hash as _hash
import phonenumbers

from src.core.database import Base


class UserRole(str, Enum):
    basic = "User"
    superuser = "Admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    other_name = Column(String)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String)
    birthday = Column(Date)
    city_id = Column(Integer, ForeignKey("cities.id"))
    additional_info = Column(Text)
    role = Column(String, nullable=False, default=UserRole.basic)

    city = relationship("City")

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError('Неверный email адрес')
        return email

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone is None:
            return phone
        try:
            parsed_phone = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError('Неверный номер телефона')
            return phone
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('Неверный номер телефона')

    @validates('birthday')
    def validate_birthday(self, key, birthday):
        if birthday is None:
            return birthday
        today = date.today()
        if birthday > today:
            raise ValueError('День рождения не может быть в будущем')
        return birthday

    def verify_password(self, password: str) -> bool:
        return _hash.bcrypt.verify(password, self.hashed_password)

    def is_superuser(self) -> bool:
        return self.role == UserRole.superuser

    def __repr__(self) -> str:
        return f'User {self.id}: {self.first_name} {self.last_name}'


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=True)

    users = relationship("User")

    def __repr__(self) -> str:
        return f'City {self.id}: {self.name}'
