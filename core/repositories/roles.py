from sqlalchemy.future import select
from sqlalchemy import update, delete
from core.models import Role
from core.dtos import CreateRole, RoleView, UpdateRole
from core.exceptions import NotFound
from .base import Repository


class RolesRepository(Repository):
    async def _get_by_id(self, role_id: int) -> Role:
        role = await self.session.get(Role, role_id)
        if not role:
            raise NotFound("Роль не найдена")
        return role

    async def create_role(self, data: CreateRole) -> Role:
        role = Role(**data.__dict__)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def get_role_by_id(self, role_id: int) -> RoleView:
        role = await self._get_by_id(role_id)
        users_ids = [user.id for user in role.users]
        return RoleView(id=role.id, title=role.title, users=users_ids)

    async def get_all_roles(self) -> list[RoleView]:
        result = await self.session.execute(select(Role))
        roles = result.scalars().all()
        role_views = [
            RoleView(
                id=role.id,
                title=role.title,
                users=[user.id for user in role.users],
            )
            for role in roles
        ]
        return role_views

    async def update_role(self, role_id: int, data: UpdateRole) -> Role:
        role = await self._get_by_id(role_id)
        role.title = data.title
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def delete_role(self, role_id: int) -> None:
        role = await self._get_by_id(role_id)
        await self.session.delete(role)
        await self.session.commit()
