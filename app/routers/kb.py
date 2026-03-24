from typing import Optional

from fastapi import APIRouter

from app.dependencies import KBSectionServiceDep, KBArticleServiceDep
from app.schemas.kb import (
    KBSectionCreateDTO, KBSectionReadDTO, KBSectionUpdateDTO,
    KBArticleCreateDTO, KBArticleReadDTO, KBArticleUpdateDTO,
)

router = APIRouter(tags=["Knowledge Base"])


# --- Sections ---

@router.get("/kb-sections/", response_model=list[KBSectionReadDTO])
async def get_all_sections(service: KBSectionServiceDep = ...):
    return await service.get_all()


@router.get("/kb-sections/{section_id}", response_model=KBSectionReadDTO)
async def get_section(section_id: int, service: KBSectionServiceDep = ...):
    return await service.get_by_id(section_id)


@router.post("/kb-sections/", response_model=KBSectionReadDTO, status_code=201)
async def create_section(data: KBSectionCreateDTO, service: KBSectionServiceDep = ...):
    return await service.create(data)


@router.patch("/kb-sections/{section_id}", response_model=KBSectionReadDTO)
async def update_section(section_id: int, data: KBSectionUpdateDTO, service: KBSectionServiceDep = ...):
    return await service.update(section_id, data)


@router.delete("/kb-sections/{section_id}", status_code=204)
async def delete_section(section_id: int, service: KBSectionServiceDep = ...):
    await service.delete(section_id)


# --- Articles ---

@router.get("/kb-articles/", response_model=list[KBArticleReadDTO])
async def get_all_articles(section_id: Optional[int] = None, service: KBArticleServiceDep = ...):
    return await service.get_all(section_id=section_id)


@router.get("/kb-articles/{article_id}", response_model=KBArticleReadDTO)
async def get_article(article_id: int, service: KBArticleServiceDep = ...):
    return await service.get_by_id(article_id)


@router.post("/kb-articles/", response_model=KBArticleReadDTO, status_code=201)
async def create_article(data: KBArticleCreateDTO, service: KBArticleServiceDep = ...):
    return await service.create(data)


@router.patch("/kb-articles/{article_id}", response_model=KBArticleReadDTO)
async def update_article(article_id: int, data: KBArticleUpdateDTO, service: KBArticleServiceDep = ...):
    return await service.update(article_id, data)


@router.delete("/kb-articles/{article_id}", status_code=204)
async def delete_article(article_id: int, service: KBArticleServiceDep = ...):
    await service.delete(article_id)
