from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.kb_section import KBSection
from app.models.kb_article import KBArticle
from app.repositories.kb_repository import KBSectionRepository, KBArticleRepository
from app.schemas.kb import (
    KBSectionCreateDTO, KBSectionReadDTO, KBSectionUpdateDTO,
    KBArticleCreateDTO, KBArticleReadDTO, KBArticleUpdateDTO,
)


class KBSectionService:
    def __init__(self, repo: KBSectionRepository):
        self.repo = repo

    async def _get_or_404(self, section_id: int) -> KBSection:
        obj = await self.repo.get_by_id(section_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"KBSection {section_id} not found")
        return obj

    async def get_by_id(self, section_id: int) -> KBSectionReadDTO:
        return KBSectionReadDTO.model_validate(await self._get_or_404(section_id))

    async def get_all(self) -> list[KBSectionReadDTO]:
        items = await self.repo.get_all()
        return [KBSectionReadDTO.model_validate(s) for s in items]

    async def create(self, data: KBSectionCreateDTO) -> KBSectionReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBSection creation error")
        return KBSectionReadDTO.model_validate(obj)

    async def update(self, section_id: int, data: KBSectionUpdateDTO) -> KBSectionReadDTO:
        obj = await self._get_or_404(section_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBSection update error")
        return KBSectionReadDTO.model_validate(obj)

    async def delete(self, section_id: int) -> None:
        obj = await self._get_or_404(section_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBSection delete error")


class KBArticleService:
    def __init__(self, repo: KBArticleRepository):
        self.repo = repo

    async def _get_or_404(self, article_id: int) -> KBArticle:
        obj = await self.repo.get_by_id(article_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"KBArticle {article_id} not found")
        return obj

    async def get_by_id(self, article_id: int) -> KBArticleReadDTO:
        return KBArticleReadDTO.model_validate(await self._get_or_404(article_id))

    async def get_all(self, section_id: Optional[int] = None) -> list[KBArticleReadDTO]:
        items = await self.repo.get_all(section_id=section_id)
        return [KBArticleReadDTO.model_validate(a) for a in items]

    async def create(self, data: KBArticleCreateDTO) -> KBArticleReadDTO:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced section not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle creation error")
        return KBArticleReadDTO.model_validate(obj)

    async def update(self, article_id: int, data: KBArticleUpdateDTO) -> KBArticleReadDTO:
        obj = await self._get_or_404(article_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle update error")
        return KBArticleReadDTO.model_validate(obj)

    async def delete(self, article_id: int) -> None:
        obj = await self._get_or_404(article_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle delete error")
