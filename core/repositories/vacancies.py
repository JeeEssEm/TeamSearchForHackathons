from sqlalchemy import insert, delete, select

from .base import Repository
from core import models
from core.dtos import CreateVacancy, Vacancy, VacancyView
from core.exceptions import NotFound


class VacanciesRepository(Repository):
    async def _get_by_id(self, vacancy_id: int) -> models.Vacancy:
        vac = await self.session.get(models.Vacancy, vacancy_id)
        if not vac:
            raise NotFound("Такой вакансии не существует")
        return vac

    async def add_technologies(self, vacancy_id: int, techs: list[int]):
        stmt = insert(models.vacancies_technologies).values(
            [
                {
                    "technology_id": tech,
                    "vacancy_id": vacancy_id,
                }
                for tech in techs
            ]
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_all_technologies(self, vacancy_id: int):
        stmt = delete(models.vacancies_technologies).where(
            models.vacancies_technologies.c.vacancy_id == vacancy_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def create_vacancy(self, data: CreateVacancy) -> VacancyView:
        vac = models.Vacancy(
            role_id=data.role_id,
            team_id=data.team_id,
            description=data.description,
            is_private=False,
        )
        self.session.add(vac)
        await self.session.commit()
        return await vac.convert_to_dto_view()

    async def get_by_id(self, vacancy_id: int) -> VacancyView:
        vac = await self._get_by_id(vacancy_id)
        return await vac.convert_to_dto_view()

    async def edit(self, vacancy_id: int, data: CreateVacancy) -> VacancyView:
        vac = await self._get_by_id(vacancy_id)
        vac.description = data.description or vac.description
        vac.role_id = data.role_id or vac.role_id
        await self.session.commit()
        return await vac.convert_to_dto_view()

    async def delete(self, vacancy_id: int):
        vac = await self._get_by_id(vacancy_id)
        await self.session.delete(vac)
        await self.session.commit()