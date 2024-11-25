from django.http import HttpResponse, HttpRequest

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container


@inject
async def index(request: HttpRequest,
                technology_service=Provide[Container.technology_service],
                db=Provide[Container.db]):

    try:
        await technology_service.create_technology('django tech')
    except Exception:
        await db.init_models()

    return HttpResponse('Object created')
