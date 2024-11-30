from .base import Service
from core.repositories import TeamsRepository
from core.dtos import Team, CreateTeam, Hackathon


class TeamsService(Service):
    repository: TeamsRepository

    async def create_team(self, data: CreateTeam) -> Team:
        team = await self.repository.create(data)
        await self.repository.add_hacks_to_team(team.id, data.hacks)
        return await self.repository.get_team_by_id(team.id)

    async def add_hacks_to_team(self, team_id: int, hacks: list[int]) -> Team:
        await self.repository.add_hacks_to_team(team_id, hacks)
        return await self.repository.get_team_by_id(team_id)
