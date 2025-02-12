from typing import AsyncIterable

from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import (
    AsyncClientSession as AsyncMongoSession,
)
from pytest import fixture

from aqua.infrastructure.periphery.pymongo.clients import (
    client_with,
)
from aqua.infrastructure.periphery.pymongo.document import Document


@fixture(scope="session")
async def mongo_client() -> AsyncIterable[AsyncMongoClient[Document]]:
    client = client_with(read_preference="primary")
    yield client
    await client.close()


@fixture(scope="session")
async def mongo_session(
    mongo_client: AsyncMongoClient[Document],
) -> AsyncIterable[AsyncMongoSession]:
    async with mongo_client.start_session() as session:
        yield session


@fixture
async def empty_mongo(
    mongo_client: AsyncMongoClient[Document],
    mongo_session: AsyncMongoSession,
) -> None:
    await mongo_client.db.users.delete_many(
        {}, session=mongo_session, comment="clear test users"
    )


@fixture
async def full_mongo(
    empty_mongo: None,  # noqa: ARG001
    mongo_client: AsyncMongoClient[Document],
    mongo_session: AsyncMongoSession,
    user_documents: list[Document],
) -> None:
    await mongo_client.db.users.insert_many(
        user_documents, session=mongo_session, comment="add test users"
    )
