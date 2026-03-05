from fastapi import APIRouter

from app.dependencies import NotificationServiceDep
from app.schemas.notification import NotificationCreateDTO, NotificationReadDTO, NotificationUpdateDTO

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationReadDTO])
async def get_all(service: NotificationServiceDep):
    return await service.get_all()


@router.get("/{notification_id}", response_model=NotificationReadDTO)
async def get_by_id(notification_id: int, service: NotificationServiceDep):
    return await service.get_by_id(notification_id)


@router.post("/", response_model=NotificationReadDTO, status_code=201)
async def create(data: NotificationCreateDTO, service: NotificationServiceDep):
    return await service.create(data)


@router.patch("/{notification_id}", response_model=NotificationReadDTO)
async def update(notification_id: int, data: NotificationUpdateDTO, service: NotificationServiceDep):
    return await service.update(notification_id, data)


@router.delete("/{notification_id}", status_code=204)
async def delete(notification_id: int, service: NotificationServiceDep):
    await service.delete(notification_id)
