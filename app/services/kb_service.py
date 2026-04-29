from typing import Optional
import uuid
import io
import os

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
from app.minio.minio_client import minio_client
from app.core.config import settings



ALLOWED_FILE_TYPES = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.ppt', '.pptx', 
                     '.png', '.jpg', '.jpeg', '.gif', '.webp', '.zip', '.rar'}
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES_PER_ARTICLE = 5


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

    def _validate_file(self, filename: str, file_size: int) -> None:
        """Проверяет расширение и размер файла"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds limit of {MAX_FILE_SIZE // (1024*1024)}MB"
            )

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Генерирует уникальное имя файла с UUID"""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())[:8]
        return f"{name}_{unique_id}{ext}"

    async def _upload_file_to_minio(self, file_content: bytes, original_filename: str) -> str:
        """Загружает файл в MinIO и возвращает путь"""
        try:
            unique_filename = self._generate_unique_filename(original_filename)
            file_path = f"kb-articles/{unique_filename}"
            
            minio_client.put_object(
                settings.MINIO_BUCKET,
                file_path,
                io.BytesIO(file_content),
                length=len(file_content),
            )
            return file_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to MinIO: {str(e)}"
            )

    async def _delete_file_from_minio(self, file_path: str) -> None:
        """Удаляет файл из MinIO"""
        try:
            minio_client.remove_object(settings.MINIO_BUCKET, file_path)
        except Exception as e:
            # Логируем ошибку но не останавливаем процесс удаления статьи
            print(f"Warning: Failed to delete file {file_path} from MinIO: {str(e)}")

    def _get_file_url(self, file_path: str) -> str:
        """Генерирует URL для скачивания файла"""
        return f"/kb-articles/attachments/{file_path}"

    async def get_by_id(self, article_id: int) -> KBArticleReadDTO:
        article = await self._get_or_404(article_id)
        article_dto = KBArticleReadDTO.model_validate(article)
        
        # Конвертируем пути в URLs
        if article.attachments:
            article_dto.attachments = [self._get_file_url(path) for path in article.attachments]
        
        return article_dto

    async def get_all(self, section_id: Optional[int] = None) -> list[KBArticleReadDTO]:
        items = await self.repo.get_all(section_id=section_id)
        result = []
        for article in items:
            article_dto = KBArticleReadDTO.model_validate(article)
            if article.attachments:
                article_dto.attachments = [self._get_file_url(path) for path in article.attachments]
            result.append(article_dto)
        return result

    async def create(self, data: KBArticleCreateDTO, files: Optional[list] = None) -> KBArticleReadDTO:
        """Создает статью и загружает прикрепленные файлы"""
        # Валидация и загрузка файлов
        uploaded_file_paths = []
        if files:
            if len(files) > MAX_FILES_PER_ARTICLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum {MAX_FILES_PER_ARTICLE} files allowed per article"
                )
            
            for file in files:
                # Читаем содержимое файла
                file_content = await file.read()
                self._validate_file(file.filename, len(file_content))
                
                # Загружаем в MinIO
                file_path = await self._upload_file_to_minio(file_content, file.filename)
                uploaded_file_paths.append(file_path)
        
        # Создаем запись в БД
        try:
            obj = await self.repo.create(data, attachments=uploaded_file_paths)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            # Удаляем загруженные файлы при ошибке
            for file_path in uploaded_file_paths:
                await self._delete_file_from_minio(file_path)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced section not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            # Удаляем загруженные файлы при ошибке
            for file_path in uploaded_file_paths:
                await self._delete_file_from_minio(file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle creation error")
        
        article_dto = KBArticleReadDTO.model_validate(obj)
        if obj.attachments:
            article_dto.attachments = [self._get_file_url(path) for path in obj.attachments]
        return article_dto

    async def update(self, article_id: int, data: KBArticleUpdateDTO, new_files: Optional[list] = None) -> KBArticleReadDTO:
        """Обновляет статью и файлы"""
        obj = await self._get_or_404(article_id)
        old_attachments = obj.attachments or []
        
        # Загружаем новые файлы если есть
        new_file_paths = []
        if new_files:
            if len(new_files) > MAX_FILES_PER_ARTICLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum {MAX_FILES_PER_ARTICLE} files allowed per article"
                )
            
            for file in new_files:
                file_content = await file.read()
                self._validate_file(file.filename, len(file_content))
                file_path = await self._upload_file_to_minio(file_content, file.filename)
                new_file_paths.append(file_path)
        
        try:
            # Определяем какие файлы оставить
            # Если new_files указаны, используем их; иначе сохраняем старые
            updated_attachments = new_file_paths if new_files else old_attachments
            
            obj = await self.repo.update(obj, data, attachments=updated_attachments)
            await self.repo.session.commit()
            
            # Удаляем старые файлы если были загружены новые
            if new_files:
                for old_path in old_attachments:
                    await self._delete_file_from_minio(old_path)
        except SQLAlchemyError:
            await self.repo.session.rollback()
            # Удаляем загруженные новые файлы при ошибке
            for file_path in new_file_paths:
                await self._delete_file_from_minio(file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle update error")
        
        article_dto = KBArticleReadDTO.model_validate(obj)
        if obj.attachments:
            article_dto.attachments = [self._get_file_url(path) for path in obj.attachments]
        return article_dto

    async def delete(self, article_id: int) -> None:
        """Удаляет статью и все прикрепленные файлы"""
        obj = await self._get_or_404(article_id)
        
        try:
            # Удаляем файлы из MinIO
            if obj.attachments:
                for file_path in obj.attachments:
                    await self._delete_file_from_minio(file_path)
            
            # Удаляем запись из БД
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="KBArticle delete error")
