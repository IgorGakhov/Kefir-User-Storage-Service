from typing import List, Tuple, Optional, NewType

from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import Base
from src.users import schemas
from src.users.models import User, City


UsersWithCities = NewType(
    'UsersWithCities',
    Tuple[List[schemas.UsersListElementModel],
          List[schemas.CitiesHintModel]]
)


def get_user_by_id(id: int, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.id == id).first()
    return user


def get_user_by_login(login: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.email == login).first()
    return user


def get_city_by_id(id: int, db: Session) -> Optional[City]:
    city = db.query(City).filter(City.id == id).first()
    return city


def update_db_model_instance_fields(model_instance: Base,
                                    update_instance_data: BaseModel) -> Base:
    '''Обновление полей объекта модели в соответствии с данными запроса'''
    for field, value in update_instance_data.dict().items():
        if value is not None:
            setattr(model_instance, field, value)
    return model_instance


def get_users_list_with_cities_hint(page: int,
                                    size: int,
                                    db: Session) -> UsersWithCities:
    # Получаем номер первого элемента на странице
    first_item = (page - 1) * size
    # Получаем список пользователей, соответствующих текущей странице и размеру
    db_users = db.query(User).limit(size).offset(first_item).all()
    # Создаем список пользователей по Pydantic схеме
    users: List[schemas.UsersListElementModel] = []
    cities_hint: List[schemas.CitiesHintModel] = []
    for db_user in db_users:
        user_model = schemas.UsersListElementModel(
            id=db_user.id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email
        )
        users.append(user_model)
        if db_user.city_id:
            city_hint = schemas.CitiesHintModel(
                id=db_user.city_id,
                name=db_user.city.name
            )
            cities_hint.append(city_hint)
    return users, cities_hint


def update_in_db(model_instance: Base, db: Session) -> None:
    db.commit()
    db.refresh(model_instance)


def add_in_db(model_instance: Base, db: Session) -> None:
    db.add(model_instance)
    db.commit()
    db.refresh(model_instance)


def delete_in_db(model_instance: Base, db: Session) -> None:
    db.delete(model_instance)
    db.commit()
