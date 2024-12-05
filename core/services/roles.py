from .base import Service
from core.repositories import RolesRepository
from core.dtos import CreateRole, RoleView, UpdateRole


class RolesService(Service):
    repository: RolesRepository

    async def create_role(self, data: CreateRole) -> RoleView:
        role = await self.repository.create_role(data)
        return await self.repository.get_role_by_id(role.id)

    async def get_role(self, role_id: int) -> RoleView:
        return await self.repository.get_role_by_id(role_id)

    async def update_role(self, role_id: int, data: UpdateRole) -> RoleView:
        updated_role = await self.repository.update_role(role_id, data)
        return await self.repository.get_role_by_id(updated_role.id)

    async def remove_role(self, role_id: int):
        await self.repository.delete_role(role_id)
