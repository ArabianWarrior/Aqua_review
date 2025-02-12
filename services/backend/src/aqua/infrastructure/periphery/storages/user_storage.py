from copy import deepcopy
from datetime import date
from typing import Iterable
from uuid import UUID

from aqua.domain.framework.entity import Entities, FrozenEntities
from aqua.domain.model.core.aggregates.user.internal.entities.day import Day
from aqua.domain.model.core.aggregates.user.internal.entities.record import (
    Record,
)
from aqua.domain.model.core.aggregates.user.root import User


class Error(Exception): ...


class NoEntityToUpdateError(Error): ...


class InMemoryUserStorage:
    def __init__(self) -> None:
        self.__users = Entities[User]()
        self.__days = Entities[Day]()
        self.__records = Entities[Record]()

    @property
    def users(self) -> FrozenEntities[User]:
        return FrozenEntities(map(deepcopy, self.__users))

    @property
    def days(self) -> FrozenEntities[Day]:
        return FrozenEntities(map(deepcopy, self.__days))

    @property
    def records(self) -> FrozenEntities[Record]:
        return FrozenEntities(map(deepcopy, self.__records))

    def add_user(self, user: User) -> None:
        self.__users.add(deepcopy(user))

    def add_day(self, day: Day) -> None:
        self.__days.add(deepcopy(day))

    def add_record(self, record: Record) -> None:
        self.__records.add(deepcopy(record))

    def update_user(self, user: User) -> None:
        for stored_user in self.__users:
            if stored_user.is_(user):
                self.__users.remove(stored_user)
                self.__users.add(deepcopy(user))
                return

        raise NoEntityToUpdateError

    def update_day(self, day: Day) -> None:
        for stored_day in self.__days:
            if stored_day.is_(day):
                self.__days.remove(stored_day)
                self.__days.add(deepcopy(day))
                return

        raise NoEntityToUpdateError

    def update_record(self, record: Record) -> None:
        for stored_record in self.__records:
            if stored_record.is_(record):
                self.__records.remove(stored_record)
                self.__records.add(deepcopy(record))
                return

        raise NoEntityToUpdateError

    def days_with_user_id(self, user_id: UUID) -> Iterable[Day]:
        return (deepcopy(day) for day in self.days if day.user_id == user_id)

    def day_with_user_id_and_date(
        self, *, user_id: UUID, date_: date
    ) -> Day | None:
        for day in self.__days:
            if day.user_id == user_id and day.date_ == date_:
                return deepcopy(day)

        return None

    def records_with_user_id(self, user_id: UUID) -> Iterable[Record]:
        return (
            deepcopy(record)
            for record in self.__records
            if record.user_id == user_id
        )

    def user_with_id(self, user_id: UUID) -> User | None:
        for user in self.__users:
            if user.id == user_id:
                return deepcopy(user)

        return None
