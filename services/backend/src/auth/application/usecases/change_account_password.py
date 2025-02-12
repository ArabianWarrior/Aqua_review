from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Literal, TypeAlias
from uuid import UUID

from result import Err, Ok, Result

from auth.application.output.log_effect import log_effect
from auth.application.output.map_effect import Mappers, map_effect
from auth.application.ports.loggers import Logger
from auth.application.ports.mappers import MapperFactory
from auth.application.ports.repos import Accounts
from auth.application.ports.transactions import TransactionFactory
from auth.domain.framework.effects.searchable import SearchableEffect
from auth.domain.framework.result import swap
from auth.domain.models.access.aggregates import account as _account
from auth.domain.models.access.vos.password import Password


_Account: TypeAlias = _account.root.Account
_AccountName: TypeAlias = _account.internal.entities.account_name.AccountName
_Session: TypeAlias = _account.internal.entities.session.Session


@dataclass(kw_only=True, frozen=True, slots=True)
class Output:
    account: _Account
    session: _Session


@asynccontextmanager
async def change_account_password[AccountsT: Accounts](
    account_id: UUID,
    new_password_text: str,
    session_id: UUID,
    *,
    accounts: AccountsT,
    account_mapper_in: MapperFactory[AccountsT, _Account],
    account_name_mapper_in: MapperFactory[AccountsT, _AccountName],
    session_mapper_in: MapperFactory[AccountsT, _Session],
    transaction_for: TransactionFactory[AccountsT],
    logger: Logger,
) -> AsyncIterator[
    Result[
        Output,
        Literal[
            "no_account",
            "no_session_for_password_change",
            "password_too_short",
            "password_contains_only_small_letters",
            "password_contains_only_capital_letters",
            "password_contains_only_digits",
            "password_has_no_numbers",
        ],
    ]
]:
    match Password.with_(text=new_password_text):
        case Ok(v):
            new_password = v
        case Err(v) as r:
            yield r
            return

    async with transaction_for(accounts) as transaction:
        account = await accounts.account_with_id(account_id)

        if not account:
            await transaction.rollback()
            yield Err("no_account")
            return

        effect = SearchableEffect()
        result = account.change_password(
            new_password=new_password,
            current_session_id=session_id,
            effect=effect,
        )
        await swap(result).map_async(lambda _: transaction.rollback())

        await result.map_async(
            lambda _: logger.log_password_change(account=account)
        )
        await result.map_async(lambda _: log_effect(effect, logger))
        await result.map_async(
            lambda _: map_effect(
                effect,
                Mappers(
                    (_Account, account_mapper_in(accounts)),
                    (_AccountName, account_name_mapper_in(accounts)),
                    (_Session, session_mapper_in(accounts)),
                ),
            )
        )

        yield result.map(
            lambda session: Output(account=account, session=session)
        )
