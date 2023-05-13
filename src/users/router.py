from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib import hash as _hash

import core.database as db
import core.handlers.exceptions as exc
from auth.manager import AuthJWT, check_jwt_user
from .models import User, UserRole
from . import schemas, utils


router_users = APIRouter(
    prefix='/users',
    tags=['user'],
)


@router_users.get(path='/current',
                  summary='Получение данных о текущем пользователе',
                  description=('Здесь находится вся информация, '
                               'доступная пользователю о самом себе, а так же '
                               'информация является ли он администратором'),
                  status_code=status.HTTP_200_OK,
                  response_model=schemas.CurrentUserResponseModel,
                  responses={400: {"model": exc.ErrorResponseModel},
                             401: {"model": exc.CodelessErrorResponseModel}})
def current_user(Authorize: AuthJWT = Depends(),
                 db: Session = Depends(db.get_db)):
    # Получаем объект БД пользователя, если он проходит верификацию
    auth_user = check_jwt_user(
        Authorize, db, (UserRole.basic, UserRole.superuser)
    )
    # Формирование модели ответа
    response = schemas.CurrentUserResponseModel(
        first_name=auth_user.first_name,
        last_name=auth_user.last_name,
        other_name=auth_user.other_name,
        email=auth_user.email,
        phone=auth_user.phone,
        birthday=auth_user.birthday,
        is_admin=auth_user.is_superuser()
    )
    return response


@router_users.patch(path='/current',
                    summary='Изменение данных пользователя',
                    description=('Здесь пользователь имеет возможность '
                                 'изменить свои данные'),
                    status_code=status.HTTP_200_OK,
                    response_model=schemas.UpdateUserResponseModel,
                    responses={400: {"model": exc.ErrorResponseModel},
                               401: {"model": exc.CodelessErrorResponseModel},
                               404: {"model": exc.CodelessErrorResponseModel}})
def edit_user(update_user_data: schemas.UpdateUserModel,
              Authorize: AuthJWT = Depends(),
              db: Session = Depends(db.get_db)):
    auth_user = check_jwt_user(
        Authorize, db, (UserRole.basic, UserRole.superuser)
    )
    # Обновляем поля пользователя в соответствии с данными запроса
    auth_user: User = utils.update_db_model_instance_fields(
        model_instance=auth_user,
        update_instance_data=update_user_data
    )
    # Формирование модели ответа
    response = schemas.UpdateUserResponseModel(
        id=auth_user.id,
        first_name=auth_user.first_name,
        last_name=auth_user.last_name,
        other_name=auth_user.other_name,
        email=auth_user.email,
        phone=auth_user.phone,
        birthday=auth_user.birthday
    )
    # Сохраняем изменения в базе данных
    utils.update_in_db(auth_user, db)
    return response


@router_users.get(path='',
                  summary=('Постраничное получение кратких данных '
                           'обо всех пользователях'),
                  description=('Здесь находится вся информация, доступная '
                               'пользователю о других пользователях'),
                  status_code=status.HTTP_200_OK,
                  response_model=schemas.UsersListResponseModel,
                  responses={400: {"model": exc.ErrorResponseModel},
                             401: {"model": exc.CodelessErrorResponseModel}})
def users(page: int, size: int,
          Authorize: AuthJWT = Depends(),
          db: Session = Depends(db.get_db)):
    _ = check_jwt_user(Authorize, db, (UserRole.basic, UserRole.superuser))
    total = db.query(User).count()
    users, _ = utils.get_users_list_with_cities_hint(page, size, db)
    # Создаем метаданные для пагинации
    meta = schemas.UsersListMetaDataModel(
        pagination=schemas.PaginatedMetaDataModel(
            total=total, page=page, size=size
        )
    )
    # Формирование модели ответа
    response = schemas.UsersListResponseModel(data=users, meta=meta)
    return response


router_admin = APIRouter(
    prefix='/private',
    tags=['admin'],
)


@router_admin.get(path='/users',
                  summary=('Постраничное получение кратких данных '
                           'обо всех пользователях'),
                  description=('Здесь находится вся информация, доступная '
                               'пользователю о других пользователях'),
                  status_code=status.HTTP_200_OK,
                  response_model=schemas.PrivateUsersListResponseModel,
                  responses={400: {"model": exc.ErrorResponseModel},
                             401: {"model": exc.CodelessErrorResponseModel},
                             403: {"model": exc.CodelessErrorResponseModel}})
def private_users(page: int, size: int,
                  Authorize: AuthJWT = Depends(),
                  db: Session = Depends(db.get_db)):
    _ = check_jwt_user(Authorize, db, (UserRole.superuser))
    total = db.query(User).count()
    users, cities_hint = utils.get_users_list_with_cities_hint(page, size, db)
    # Создаем метаданные для пагинации
    meta = schemas.PrivateUsersListMetaDataModel(
        pagination=schemas.PaginatedMetaDataModel(
            total=total, page=page, size=size
        ),
        hint=schemas.PrivateUsersListHintMetaModel(city=cities_hint)
    )
    # Формирование модели ответа
    response = schemas.PrivateUsersListResponseModel(data=users, meta=meta)
    return response


@router_admin.post(path='/users',
                   summary='Создание пользователя',
                   description=('Здесь возможно занести в базу '
                                'нового пользователя '
                                'с минимальной информацией о нем'),
                   status_code=status.HTTP_201_CREATED,
                   response_model=schemas.PrivateDetailUserResponseModel,
                   responses={400: {"model": exc.ErrorResponseModel},
                              401: {"model": exc.CodelessErrorResponseModel},
                              403: {"model": exc.CodelessErrorResponseModel}})
def private_create_users(create_user_data: schemas.PrivateCreateUserModel,
                         Authorize: AuthJWT = Depends(),
                         db: Session = Depends(db.get_db)):
    _ = check_jwt_user(Authorize, db, (UserRole.superuser))
    # Проверяем, есть ли пользователь с введенным логином в базе данных
    db_user = utils.get_user_by_login(create_user_data.email, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=('Пользователь с таким логином уже существует. '
                    'Придумайте другой и попробуйте снова.'))
    user_role = UserRole.superuser if create_user_data.is_admin else UserRole.basic  # noqa: E501
    # Проверяем, есть ли город с введенным ID в базе данных
    user_home_city = utils.get_city_by_id(create_user_data.city, db)
    if create_user_data.city and not user_home_city:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=('Города с таким ID нет в базе данных.'))
    city_id = user_home_city.id if user_home_city else None
    # Создаем нового пользователя и добавляем его в базу данных
    hashed_user_password = _hash.bcrypt.hash(create_user_data.password)
    db_user = User(first_name=create_user_data.first_name,
                   last_name=create_user_data.last_name,
                   other_name=create_user_data.other_name,
                   email=create_user_data.email,
                   phone=create_user_data.phone,
                   birthday=create_user_data.birthday,
                   city_id=city_id,
                   additional_info=create_user_data.additional_info,
                   role=user_role,
                   hashed_password=hashed_user_password)
    # Формирование модели ответа
    response = schemas.PrivateDetailUserResponseModel(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        other_name=db_user.other_name,
        email=db_user.email,
        phone=db_user.phone,
        birthday=db_user.birthday,
        city=db_user.city_id,
        additional_info=db_user.additional_info,
        is_admin=db_user.is_superuser(),
    )
    # Добавляем изменения в базе данных
    utils.add_in_db(db_user, db)
    return response


@router_admin.get(path='/users/{pk}',
                  summary='Детальное получение информации о пользователе',
                  description=('Здесь администратор может увидеть '
                               'всю существующую пользовательскую информацию'),
                  status_code=status.HTTP_200_OK,
                  response_model=schemas.PrivateDetailUserResponseModel,
                  responses={400: {"model": exc.ErrorResponseModel},
                             401: {"model": exc.CodelessErrorResponseModel},
                             403: {"model": exc.CodelessErrorResponseModel},
                             404: {"model": exc.CodelessErrorResponseModel}})
def private_get_user(pk: int,
                     Authorize: AuthJWT = Depends(),
                     db: Session = Depends(db.get_db)):
    _ = check_jwt_user(Authorize, db, (UserRole.superuser))
    db_user = utils.get_user_by_id(pk, db)
    # Формирование модели ответа
    response = schemas.PrivateDetailUserResponseModel(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        other_name=db_user.other_name,
        email=db_user.email,
        phone=db_user.phone,
        birthday=db_user.birthday,
        city=db_user.city_id,
        additional_info=db_user.additional_info,
        is_admin=db_user.is_superuser(),
    )
    return response


@router_admin.delete(path='/users/{pk}',
                     summary='Удаление пользователя',
                     description='Удаление пользователя',
                     status_code=status.HTTP_204_NO_CONTENT,
                     responses={401: {"model": exc.CodelessErrorResponseModel},
                                403: {"model": exc.CodelessErrorResponseModel}})
def private_delete_user(pk: int,
                        Authorize: AuthJWT = Depends(),
                        db: Session = Depends(db.get_db)):
    _ = check_jwt_user(Authorize, db, (UserRole.superuser))
    db_user = utils.get_user_by_id(pk, db)
    if db_user:
        utils.delete_in_db(db_user, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователя с таким ID не существует.')


@router_admin.patch(path='/users/{pk}',
                    summary='Изменение информации о пользователе',
                    description=('Здесь администратор может изменить '
                                 'любую информацию о пользователе'),
                    status_code=status.HTTP_200_OK,
                    response_model=schemas.PrivateDetailUserResponseModel,
                    responses={400: {"model": exc.ErrorResponseModel},
                               401: {"model": exc.CodelessErrorResponseModel},
                               403: {"model": exc.CodelessErrorResponseModel},
                               404: {"model": exc.CodelessErrorResponseModel}})
def private_patch_user(pk: int,
                       update_user_data: schemas.PrivateUpdateUserModel,
                       Authorize: AuthJWT = Depends(),
                       db: Session = Depends(db.get_db)):
    auth_user = check_jwt_user(Authorize, db, (UserRole.superuser))
    db_user = utils.get_user_by_id(pk, db)
    # Проверяем, есть ли пользователь с введенным логином в базе данных
    if utils.get_user_by_login(update_user_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=('Пользователь с таким логином уже существует. '
                    'Придумайте другой и попробуйте снова.'))
    # Обновляем поля пользователя в соответствии с данными запроса
    auth_user: User = utils.update_db_model_instance_fields(
        model_instance=auth_user,
        update_instance_data=update_user_data
    )
    # Формирование модели ответа
    response = schemas.PrivateDetailUserResponseModel(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        other_name=db_user.other_name,
        email=db_user.email,
        phone=db_user.phone,
        birthday=db_user.birthday,
        city=db_user.city_id,
        additional_info=db_user.additional_info,
        is_admin=db_user.is_superuser(),
    )
    # Сохраняем изменения в базе данных
    utils.update_in_db(db_user, db)
    return response
