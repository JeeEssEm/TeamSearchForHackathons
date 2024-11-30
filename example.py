import asyncio
import logging
from datetime import date

from dependency_injector.wiring import Provide, inject

from core.config import settings
from core.services import TechnologiesService
from core import models
from core import dtos
from core.repositories import TeamsRepository, TechnologiesRepository
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
async def create_team(
        db=Provide[Container.db]
):
    async with db.session() as session:
        team_repo = TeamsRepository(session)
        dto = dtos.CreateTeam(
            1,
            'team 1',
            'some desc',
            [1]
        )
        team = await team_repo.create(dto)
        print(team)
        await team_repo.add_hacks_to_team(team.id, [2])
        print(await team_repo.get_team_by_id(team.id))


async def main(db=Provide[Container.db]):
    if settings.INIT_MODELS:  # если модельки в бд не созданы, то создаём...
        await db.init_models()  # об этом думать не надо

    today = date.today()
    await create_entity(models.User(
        name='name',
        middlename='middle name',
        surname='surname',
        email='email@em.ail',
        uni='miem', year_of_study=-1, group='biv248',
        about_me='it feels so empty without me',
        telegram_id=123123
    ))
    await create_entity(models.Hackathon(title='test hack 1', start_date=today,
                                         end_date=today, id=1))
    await create_entity(models.Hackathon(title='test hack 2', start_date=today,
                                         end_date=today, id=2))

    await create_team()


if __name__ == "__main__":
    # тут ниче не трогать. Почти все эти вещи уже прописаны в определённых
    # местах
    container = Container()
    container.wire(modules=[__name__])

    logging.disable(logging.INFO)

    asyncio.run(main())
