import asyncio
import logging
from datetime import date

from dependency_injector.wiring import Provide, inject

from core.config import settings
from core import models
from core import dtos
from core.repositories import (TeamsRepository, TechnologiesRepository,
                               UsersRepository)
from core.services import TeamsService
from core.dependencies.container import Container


@inject
async def create_entity(
    model,
    db=Provide[Container.db],
):
    async with db.session() as session:
        session.add(model)
        await session.commit()


@inject
async def create_team(db=Provide[Container.db]):
    async with db.session() as session:
        team_repo = TeamsService(session)
        dto = dtos.CreateTeam(1, "team 1", "some desc", [1])
        team = await team_repo.create_team(dto, 1)
        await team_repo.add_hacks_to_team(team.id, [2])
        # print(await team_repo.get_by_id(team.id))


@inject
async def test(db=Provide[Container.db]):
    async with db.session() as session:
        team_repo = TechnologiesRepository(session)
        print(await team_repo.get_technologies(10, 1))


@inject
async def get_teams_test(db=Provide[Container.db]):
    async with db.session() as session:
        team_repo = UsersRepository(session)
        print(await team_repo.get_teams(1))


async def main(db=Provide[Container.db]):
    if settings.INIT_MODELS:  # если модельки в бд не созданы, то создаём...
        await db.init_models()  # об этом думать не надо

    # today = date.today()
    # await create_entity(
    #     models.User(
    #         name="name",
    #         middlename="middle name",
    #         surname="surname",
    #         uni="miem",
    #         year_of_study=-1,
    #         group="biv248",
    #         about_me="it feels so empty without me",
    #         telegram_id=123123,
    #     )
    # )
    # await create_entity(
    #     models.Hackathon(
    #         title="test hack 1", start_date=today, end_date=today, id=1
    #     )
    # )
    # await create_entity(
    #     models.Hackathon(
    #         title="test hack 2", start_date=today, end_date=today, id=2
    #     )
    # )
    # await create_entity(
    #     models.Technology(
    #         title="test hack 1"
    #     )
    # )
    # await create_entity(
    #     models.Technology(
    #         title="test hack 2"
    #     )
    # )
    #
    # await create_team()

    # await test()
    # await create_team()
    # await get_teams_test()


if __name__ == "__main__":
    # тут ниче не трогать. Почти все эти вещи уже прописаны в определённых
    # местах
    container = Container()
    container.wire(modules=[__name__])

    # logging.disable(logging.INFO)

    asyncio.run(main())
