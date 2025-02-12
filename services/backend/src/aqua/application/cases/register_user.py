from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator
from uuid import UUID

from result import Err, Ok, Result

from aqua.application.output.output_effect import output_effect
from aqua.application.ports import loggers, repos, views
from aqua.application.ports.mappers import (
    DayMapperTo,
    RecordMapperTo,
    UserMapperTo,
)
from aqua.application.ports.transactions import TransactionFor
from aqua.domain.framework.effects.searchable import SearchableEffect
from aqua.domain.framework.fp.result import ErrList, OkList, rlist
from aqua.domain.model.access.entities.user import User as AccessUser
from aqua.domain.model.core.aggregates.user.root import (
    NoWeightForSuitableWaterBalanceError,
    User,
)
from aqua.domain.model.core.vos.glass import Glass
from aqua.domain.model.core.vos.target import Target
from aqua.domain.model.core.vos.water_balance import (
    ExtremeWeightForSuitableWaterBalanceError,
    WaterBalance,
)
from aqua.domain.model.primitives.vos.water import Water
from aqua.domain.model.primitives.vos.weight import Weight


@dataclass(kw_only=True, frozen=True, slots=True)
class NegativeTargetWaterBalanceMillilitersError: ...


@dataclass(kw_only=True, frozen=True, slots=True)
class NegativeGlassMillilitersError: ...


@dataclass(kw_only=True, frozen=True, slots=True)
class NegativeWeightKilogramsError: ...


@asynccontextmanager
async def register_user[UsersT: repos.Users, ViewT](
    user_id: UUID,
    target_water_balance_milliliters: int | None,
    glass_milliliters: int | None,
    weight_kilograms: int | None,
    *,
    view_of: views.RegistrationViewOf[ViewT],
    users: UsersT,
    transaction_for: TransactionFor[UsersT],
    logger: loggers.Logger,
    user_mapper_to: UserMapperTo[UsersT],
    day_mapper_to: DayMapperTo[UsersT],
    record_mapper_to: RecordMapperTo[UsersT],
) -> AsyncIterator[
    Result[
        ViewT,
        (
            ExtremeWeightForSuitableWaterBalanceError
            | NoWeightForSuitableWaterBalanceError
            | NegativeTargetWaterBalanceMillilitersError
            | NegativeGlassMillilitersError
            | NegativeWeightKilogramsError
        ),
    ]
]:
    target_result: Result[
        Target | None, NegativeTargetWaterBalanceMillilitersError
    ]
    weight_result: Result[Weight | None, NegativeWeightKilogramsError]
    glass_result: Result[Glass | None, NegativeGlassMillilitersError]

    if target_water_balance_milliliters is None:
        target_result = Ok(None)
    else:
        target_result = (
            Water.with_(milliliters=target_water_balance_milliliters)
            .map_err(lambda _: NegativeTargetWaterBalanceMillilitersError())
            .map(lambda water: Target(water_balance=WaterBalance(water=water)))
        )

    if weight_kilograms is None:
        weight_result = Ok(None)
    else:
        weight_result = Weight.with_(kilograms=weight_kilograms).map_err(
            lambda _: NegativeWeightKilogramsError()
        )

    if glass_milliliters is None:
        glass_result = Ok(None)
    else:
        glass_result = (
            Water.with_(milliliters=glass_milliliters)
            .map_err(lambda _: NegativeGlassMillilitersError())
            .map(lambda water: Glass(capacity=water))
        )

    match rlist(target_result) + rlist(glass_result) + rlist(weight_result):
        case ErrList(error):
            yield Err(error)
            return
        case OkList(list_):
            target, glass, weight = list_

    effect = SearchableEffect()

    async with transaction_for(users):
        user = await users.user_with_id(user_id)

        if user is not None:
            await logger.log_registered_user_registration(user)
            yield Ok(view_of(user))
            return

        user_result = User.translated_from(
            AccessUser(id=user_id, events=list()),
            weight=weight,
            glass=glass,
            target=target,
            effect=effect,
        )

        await user_result.map_async(
            lambda _: output_effect(
                effect,
                user_mapper=user_mapper_to(users),
                day_mapper=day_mapper_to(users),
                record_mapper=record_mapper_to(users),
                logger=logger,
            )
        )

        yield user_result.map(lambda user: view_of(user))
