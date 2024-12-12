from datetime import date

from sqlalchemy import insert, delete, update, select

from .base import Repository
from core import models
from core.dtos import CreateTeam, Team, BaseTeam, EditTeam
from core.exceptions import NotFound


class TeamsRepository(Repository):
    async def _get_team_by_id(self, team_id: int) -> models.Team:
        team = await self.session.get(models.Team, team_id)
        if not team:
            raise NotFound(f"Команда id={team_id} не существует")
        return team

    async def add_hacks_to_team(self, team_id: int, hacks: list[int]):
        stmt = insert(models.teams_hackathons).values(
            [{"team_id": team_id, "hackathon_id": hack_id} for hack_id in hacks]
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def create(self, data: CreateTeam) -> Team:
        team = models.Team(
            title=data.title,
            description=data.description,
            is_private=False,
            captain_id=data.captain_id,
        )
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return await team.convert_to_dto()

    async def get_by_id(self, team_id: int) -> Team:
        team = await self._get_team_by_id(team_id)
        dto = await team.convert_to_dto()
        member_ids = list(map(lambda m: m.id, team.members))
        # чтобы подтянуть роль юзера в конкретной команде, приходится исполнять
        # такое:
        stmt = (select(models.users_teams, models.Role)
                .join(models.Role)
                .distinct()
                .where(
            models.users_teams.c.team_id == team.id,
            models.users_teams.c.user_id.in_(member_ids)
        ))
        # рот твой вертел. Почему нельзя было сделать users_teams сущностью??
        # вот упёрся тебе этот association_table
        res = await self.session.execute(stmt)

        # проходим по всем юзерам и ставим ему найденную роль
        for row in res:
            for user in dto.members:
                if row[0] == user.id:
                    user.role = row[-1].title
        return dto

    async def edit(self, team_id: int, data: EditTeam) -> Team:
        team = await self._get_team_by_id(team_id)
        team.title = data.title or team.title
        team.description = data.description or team.description
        await self.session.commit()
        return await team.convert_to_dto()

    async def add_user_to_team(self, team_id: int, user_id: int, role_id: int):
        stmt = insert(models.users_teams).values(
            team_id=team_id, user_id=user_id, role_id=role_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def change_capitan(self, team_id: int, captain_id: int):
        team = await self._get_team_by_id(team_id)
        team.captain_id = captain_id
        await self.session.commit()

    async def remove_user(self, team_id: int, user_id: int):
        stmt = delete(models.users_teams).where(
            models.users_teams.c.team_id == team_id,
            models.users_teams.c.user_id == user_id,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def edit_user_role(self, team_id: int, user_id: int, role_id: int):
        stmt = (
            update(models.users_teams)
            .where(
                models.users_teams.c.team_id == team_id,
                models.users_teams.c.user_id == user_id,
            )
            .values(role_id=role_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_base_team(self, team_id: int) -> BaseTeam:
        team = await self._get_team_by_id(team_id)
        return await team.convert_to_dto()

    async def remove_hacks(self, team_id: int, hacks: list[int]):
        stmt = delete(models.teams_hackathons).where(
            models.teams_hackathons.c.hackathon_id.in_(hacks),
            models.teams_hackathons.c.team_id == team_id,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_all_hacks(self, team_id: int):
        stmt = delete(models.teams_hackathons).where(
            models.teams_hackathons.c.team_id == team_id,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_team(self, team_id: int):
        stmt = delete(models.Team).where(models.Team.id == team_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_old_hacks(self, team_id: int):
        today = date.today()
        sub_q = select(models.Hackathon.id).where(
            models.Hackathon.end_date < today
        )
        stmt = delete(models.teams_hackathons).where(
            models.teams_hackathons.c.team_id == team_id,
            models.teams_hackathons.c.hackathon_id.in_(sub_q)
        )
        await self.session.execute(stmt)
        await self.session.commit()
