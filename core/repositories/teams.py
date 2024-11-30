from sqlalchemy import insert

from .base import Repository
from core import models
from core.dtos import CreateTeam, Team, Hackathon


class TeamsRepository(Repository):
    async def _get_team_by_id(self, team_id: int) -> models.Team:
        team = await self.session.get(models.Team, team_id)
        if not team:
            raise IndexError(f'Команда id={team_id} не существует')
        return team

    async def add_hacks_to_team(self, team_id: int, hacks: list[int]):
        stmt = insert(models.teams_hackathons).values([
            {'team_id': team_id, 'hackathon_id': hack_id} for hack_id in hacks
        ])
        await self.session.execute(stmt)
        await self.session.commit()

    async def create(self, data: CreateTeam) -> Team:
        team = models.Team(
            title=data.title,
            description=data.description,
            is_private=False,
            captain_id=data.captain_id
        )
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return await team.convert_to_dto()

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await self._get_team_by_id(team_id)
        return await team.convert_to_dto()
