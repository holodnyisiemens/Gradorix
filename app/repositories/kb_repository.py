from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kb_section import KBSection
from app.models.kb_article import KBArticle
from app.schemas.kb import (
    KBSectionCreateDTO, KBSectionUpdateDTO,
    KBArticleCreateDTO, KBArticleUpdateDTO,
)


class KBSectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, section_id: int) -> Optional[KBSection]:
        return await self.session.get(KBSection, section_id)

    async def create(self, data: KBSectionCreateDTO) -> KBSection:
        section = KBSection(**data.model_dump())
        self.session.add(section)
        await self.session.flush()
        await self.session.refresh(section)
        return section

    async def delete(self, section: KBSection) -> None:
        await self.session.delete(section)
        await self.session.flush()

    async def update(self, section: KBSection, data: KBSectionUpdateDTO) -> KBSection:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(section, field, value)
        await self.session.flush()
        await self.session.refresh(section)
        return section

    async def get_all(self) -> list[KBSection]:
        stmt = select(KBSection).order_by(KBSection.order)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class KBArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, article_id: int) -> Optional[KBArticle]:
        return await self.session.get(KBArticle, article_id)

    async def create(self, data: KBArticleCreateDTO, attachments: Optional[list[str]] = None) -> KBArticle:
        article_data = data.model_dump()
        article_data['attachments'] = attachments or []
        article = KBArticle(**article_data)
        self.session.add(article)
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def delete(self, article: KBArticle) -> None:
        await self.session.delete(article)
        await self.session.flush()

    async def update(self, article: KBArticle, data: KBArticleUpdateDTO, attachments: Optional[list[str]] = None) -> KBArticle:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(article, field, value)
        if attachments is not None:
            article.attachments = attachments
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def get_all(self, section_id: Optional[int] = None) -> list[KBArticle]:
        stmt = select(KBArticle)
        if section_id is not None:
            stmt = stmt.where(KBArticle.section_id == section_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
