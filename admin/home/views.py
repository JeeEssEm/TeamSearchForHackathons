from django.http import HttpResponse, HttpRequest

from dependency_injector.wiring import Provide, inject

from core.dependencies.containers import ServiceContainer


@inject
async def index(request: HttpRequest,
                technology_service=Provide[ServiceContainer.technology_service],
                db=Provide[ServiceContainer.db]):

    try:
        await technology_service.create_technology('django tech')
    except Exception:
        await db.init_models()

    return HttpResponse('Object created')
