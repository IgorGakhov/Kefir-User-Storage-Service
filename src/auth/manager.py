from typing import Final

from fastapi import HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import JWTDecodeError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.config import AUTH_JWT_SECRET_KEY

from users.models import User, UserRole
from users.utils import get_user_by_id, get_user_by_login


ACCESS_TOKEN_NAME: Final[str] = 'access_token_cookie'
REFRESH_TOKEN_NAME: Final[str] = 'refresh_token_cookie'
ALGORITHM: Final[str] = 'HS256'


# Настройка JWT
# https://indominusbyte.github.io/fastapi-jwt-auth/
class Settings(BaseModel):
    authjwt_secret_key: str = AUTH_JWT_SECRET_KEY
    authjwt_algorithm: str = ALGORITHM
    authjwt_token_location: set = {'cookies'}
    authjwt_access_cookie_key: str = ACCESS_TOKEN_NAME
    authjwt_refresh_cookie_key: str = REFRESH_TOKEN_NAME
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_secure: bool = True


@AuthJWT.load_config
def get_config():
    return Settings()


def authenticate_user(login: str, password: str, db: Session) -> User:
    '''Функция аутентификации пользователя для логина.'''
    user = get_user_by_login(login, db)
    if user and not user.verify_password(password):
        user = None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Отказ в доступе. Неверные логин или пароль.'
        )
    return user


def check_jwt_user(Authorize: AuthJWT,
                   db: Session,
                   permissions: set = (UserRole.basic)) -> User:
    '''Функция проверки текущего пользователя по JWT токену.'''
    # Проверяем аутентификацию пользователя через куки
    try:
        Authorize.jwt_required()
    except JWTDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Отказ в доступе. Токен доступа недействителен.'
        )
    # Получаем идентификатор пользователя из JWT и информацию о нем
    user_id = Authorize.get_jwt_subject()
    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь недействителен'
        )
    if user.role not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для пользования этим маршрутом.'
        )
    return user
