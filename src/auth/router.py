from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

import src.core.database as db
import src.core.handlers.exceptions as exc
from src.auth.manager import AuthJWT, authenticate_user
from src.users.schemas import CurrentUserResponseModel


router = APIRouter(
    prefix='',
    tags=['auth'],
)


class LoginModel(BaseModel):
    login: EmailStr
    password: str


@router.post('/login',
             summary='Вход в систему',
             description=('После успешного входа в систему '
                          'необходимо установить Cookies для пользователя'),
             status_code=status.HTTP_200_OK,
             response_model=CurrentUserResponseModel,
             responses={400: {"model": exc.ErrorResponseModel},
                        401: {"model": exc.CodelessErrorResponseModel}})
def login(user: LoginModel,
          Authorize: AuthJWT = Depends(),
          db: Session = Depends(db.get_db)):
    # Аутентификация пользователя
    auth_user = authenticate_user(user.login, user.password, db)
    # Формирование модели ответа
    response = CurrentUserResponseModel(
        first_name=auth_user.first_name,
        last_name=auth_user.last_name,
        other_name=auth_user.other_name,
        email=auth_user.email,
        phone=auth_user.phone,
        birthday=auth_user.birthday,
        is_admin=auth_user.is_superuser()
    )
    # Создаем access и refresh токены
    current_user_subject = str(auth_user.id)
    access_token = Authorize.create_access_token(subject=current_user_subject)
    refresh_token = Authorize.create_refresh_token(subject=current_user_subject)

    # Устанавливаем cookie JWT в ответ
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return response


@router.post('/refresh',
             summary='Обновление access токена')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user_subject = Authorize.get_jwt_subject()
    new_access_token = \
        Authorize.create_access_token(subject=current_user_subject)
    # Устанавливаем cookie JWT в ответ
    Authorize.set_access_cookies(new_access_token)
    return {'msg': 'Токен доступа успешно обновлён'}


@router.get(path='/logout',
            summary='Выход из системы',
            description=('При успешном выходе '
                         'необходимо удалить установленные Cookies'),
            status_code=status.HTTP_200_OK)
def logout(Authorize: AuthJWT = Depends()):
    # Поскольку JWT теперь хранятся в HTTP-файле cookie, мы не можем
    # выйти из системы, просто удалив куки во внешнем интерфейсе.
    # Нам нужен бекенд, чтобы отправить нам ответ на удаление файлов cookie.
    Authorize.jwt_required()

    # Удаляем cookie с токенами доступа
    Authorize.unset_jwt_cookies()
