from .base import Service
from core.repositories import TeamsRepository
from core.dtos import Team, CreateTeam, EditTeam


class TeamsService(Service):
    repository: TeamsRepository

    async def create_team(self, data: CreateTeam, captain_role_id: int) -> Team:
        team = await self.repository.create(data)
        if data.hacks:
            await self.repository.add_hacks_to_team(team.id, data.hacks)
        await self.repository.add_user_to_team(
            team.id, data.captain_id, captain_role_id
        )
        return await self.repository.get_by_id(team.id)

    async def add_hacks_to_team(self, team_id: int, hacks: list[int]) -> Team:
        await self.repository.add_hacks_to_team(team_id, hacks)
        return await self.repository.get_by_id(team_id)

    async def remove_hacks_from_team(self, team_id: int, hacks: list[int]):
        await self.repository.remove_hacks(team_id, hacks)

    async def get_team_by_id(self, team_id: int) -> Team:
        return await self.repository.get_by_id(team_id)

    async def edit_team_by_id(self, team_id: int, team: EditTeam) -> Team:
        return await self.repository.edit(team_id, team)

    async def kick(self, team_id: int, user_id: int):
        team = await self.repository.get_by_id(team_id)
        await self.repository.remove_user(team_id, user_id)
        if team.captain_id == user_id:
            await self.repository.delete_team(team_id)

    async def make_capitan(self, team_id: int, user_id: int):
        await self.repository.change_capitan(team_id, user_id)

    async def add_user_to_team(self, team_id: int, user_id: int, role_id: int):
        await self.repository.add_user_to_team(team_id, user_id, role_id)

    async def edit_user_role(self, team_id: int, user_id: int, role: int):
        await self.repository.edit_user_role(team_id, user_id, role)
