import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.sql.expression import func

from .setup import create_entity, db, test_db, drop_db
from core.services import TeamsService
from core import dtos
from core import models


async def get_team_by_id(team_id, session):
    return await session.execute(select(models.Team).where(
        models.Team.id == team_id
    ))


@pytest.mark.asyncio
async def test_create_edit_team(test_db, drop_db):
    # создание/редактирование команды
    await test_db
    await create_entity(models.User(
        name='name',
        middlename='middle name',
        surname='surname',
        email='email@em.ail',
        uni='miem', year_of_study=-1, group='biv248',
        about_me='it feels so empty without me',
        telegram_id=123123
    ))
    await create_entity(models.Role(title='backend'))
    async with db.session() as session:
        teams_service = TeamsService(session)
        # создание команды
        res = await session.execute(select(func.count()).select_from(
            models.Team
        ))
        assert res.scalar() == 0

        team = await teams_service.create_team(dtos.CreateTeam(
            title='test team', description='test team description',
            captain_id=1, hacks=[],
        ), captain_role_id=1)
        res = await session.execute(
            select(func.count()).select_from(models.Team))
        assert res.scalar() == 1
        t = await teams_service.get_team_by_id(team.id)
        assert t.title == 'test team'

        # редактирование
        await teams_service.edit_team_by_id(t.id, dtos.CreateTeam(
            title='team 2', description='other desc', captain_id=-1, hacks=[]
        ))
        t = await teams_service.get_team_by_id(team.id)
        assert t.title == 'team 2'
        assert t.description == 'other desc'
        assert t.captain_id == 1
        assert t.hacks == []

    await drop_db


@pytest.mark.asyncio
async def test_hack_team(test_db, drop_db):
    # добавить/удалить хакатоны команды
    await test_db
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
    await create_entity(models.Role(title='backend'))
    await create_entity(models.Hackathon(title='hack 1', start_date=today,
                                         end_date=today))
    await create_entity(models.Hackathon(title='hack 2', start_date=today,
                                         end_date=today))

    async with db.session() as session:
        teams_service = TeamsService(session)
        # создание команды с хаком
        team = await teams_service.create_team(dtos.CreateTeam(
            title='test team', description='test team description',
            captain_id=1, hacks=[1],
        ), captain_role_id=1)
        res = await session.execute(select(models.Team).where(
            models.Team.id == team.id
        ))
        assert len(await res.scalar().awaitable_attrs.hackathons) == 1

        # удаление хака
        await teams_service.remove_hacks_from_team(team.id, [1])
        res = await session.execute(select(models.Team).where(
            models.Team.id == team.id
        ))
        assert len(await res.scalar().awaitable_attrs.hackathons) == 0

        # добавление хаков
        await teams_service.add_hacks_to_team(team.id, [1, 2])
        res = await session.execute(select(models.Team).where(
            models.Team.id == team.id
        ))
        assert len(await res.scalar().awaitable_attrs.hackathons) == 2

    await drop_db


@pytest.mark.asyncio
async def test_users_team(test_db, drop_db):
    # добавить/кик/сделать капитаном юзера и удаление команды
    await test_db
    await create_entity(models.User(
        id=1,
        name='name',
        middlename='middle name',
        surname='surname',
        email='email@em.ail',
        uni='miem', year_of_study=-1, group='biv248',
        about_me='it feels so empty without me',
        telegram_id=123123
    ))
    await create_entity(models.User(
        id=2,
        name='other name',
        middlename='middle name',
        surname='surname',
        email='email@em.a2il',
        uni='misis', year_of_study=-2, group='biv258',
        about_me='info',
        telegram_id=123124
    ))

    await create_entity(models.Role(title='backend', id=1))
    await create_entity(models.Role(title='frontend', id=2))

    async with db.session() as session:
        teams_service = TeamsService(session)
        team = await teams_service.create_team(dtos.CreateTeam(
            title='test team', description='test team description',
            captain_id=1, hacks=[],
        ), captain_role_id=1)

        res = await get_team_by_id(team.id, session)
        assert len(await res.scalar().awaitable_attrs.users) == 1
        # добавляем юзера
        await teams_service.add_user_to_team(team.id, 2, 1)
        res = (await get_team_by_id(team.id, session)).scalar()
        assert len(await res.awaitable_attrs.users) == 2

        # делаем капитаном
        assert res.captain_id == 1
        await teams_service.make_capitan(team.id, 2)
        res = (await get_team_by_id(team.id, session)).scalar()
        assert res.captain_id == 2
        # кикаем старого капитана
        res = await get_team_by_id(team.id, session)
        assert len(await res.scalar().awaitable_attrs.users) == 2
        await teams_service.kick(team.id, 1)
        res = await get_team_by_id(team.id, session)
        assert len(await res.scalar().awaitable_attrs.users) == 1

        # меняем роль юзера
        user = await session.execute(select(models.users_teams).where(
            models.users_teams.c.user_id == 2
        ))
        assert user.first().role_id == 1
        await teams_service.edit_user_role(team.id, 2, 2)
        user = await session.execute(select(models.users_teams).where(
            models.users_teams.c.user_id == 2
        ))
        assert user.first().role_id == 2

        # выкидываем единственного капитана из команды => команда уничтожится
        await teams_service.kick(team.id, 2)
        res = await session.execute(
            select(func.count()).select_from(models.Team))
        assert res.scalar() == 0

    await drop_db
