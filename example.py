import asyncio
import logging

from dependency_injector.wiring import Provide, inject

from core.config import settings
from core.services import TechnologiesService
from core.dependencies.container import Container


@inject
async def create_technology(
        tech_service: TechnologiesService =
        Provide[Container.technology_service]
):
    # вот это уже пример инъекции зависимости сервиса, работающего с
    # технологиями. Это збс, потому что вам не нужно думать, как там
    # создаётся сессия к бд. Просто получаете сервис и дёргаете нужные методы

    # зачастую вам понадобится получать сервисы и работать с ними именно таким
    # образом
    res = await tech_service.create_technology('test technology')
    print(res)


async def main(
        db=Provide[Container.db]
):
    if settings.INIT_MODELS:  # если модельки в бд не созданы, то создаём...
        await db.init_models()  # об этом думать не надо

    for _ in range(23):
        await create_technology()


if __name__ == '__main__':
    # тут ниче не трогать. Почти все эти вещи уже прописаны в определённых
    # местах
    container = Container()
    container.wire(modules=[__name__])

    logging.disable(logging.INFO)

    asyncio.run(main())
