from typing import Optional
import io
import mimetypes
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, File, UploadFile, Depends, Form
from starlette.responses import StreamingResponse

from app.dependencies import KBSectionServiceDep, KBArticleServiceDep
from app.auth.utils import get_current_user
from app.models.user import User
from app.schemas.kb import (
    KBSectionCreateDTO, KBSectionReadDTO, KBSectionUpdateDTO,
    KBArticleCreateDTO, KBArticleReadDTO, KBArticleUpdateDTO,
)
from app.minio.minio_client import minio_client
from app.core.config import settings
from fastapi import HTTPException
from starlette import status

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
async def create_article(
    section_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    created_at: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(None),
    service: KBArticleServiceDep = ...,
):
    # Парсим дату если она подана
    parsed_date = datetime.today().date()
    if created_at:
        try:
            parsed_date = datetime.strptime(created_at, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = datetime.today().date()
    
    data = KBArticleCreateDTO(
        section_id=int(section_id),
        title=title,
        content=content,
        author=author,
        created_at=parsed_date
    )
    
    return await service.create(data, files=files)


@router.patch("/kb-articles/{article_id}", response_model=KBArticleReadDTO)
async def update_article(
    article_id: int,
    section_id: Optional[int] = Form(None),
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    created_at: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(None),
    service: KBArticleServiceDep = ...
):
    parsed_date = None
    if created_at:
        try:
            parsed_date = datetime.strptime(created_at, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    data = KBArticleUpdateDTO(
        section_id=section_id,
        title=title,
        content=content,
        author=author,
        created_at=parsed_date
    )
    
    return await service.update(article_id, data, new_files=files)


@router.delete("/kb-articles/{article_id}", status_code=204)
async def delete_article(
    article_id: int,
    service: KBArticleServiceDep = ...
):
    await service.delete(article_id)


# --- File Download ---

@router.get("/kb-articles/attachments/{file_path:path}")
async def download_attachment(
    file_path: str
):
    """Скачивает прикрепленный файл из MinIO"""
    try:
        object_key = file_path.lstrip("/")
        if not object_key.startswith("kb-articles/"):
            object_key = f"kb-articles/{object_key}"

        response = minio_client.get_object(settings.MINIO_BUCKET, object_key)
        
        file_content = response.read()
        
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        filename = file_path.split("/")[-1]
        safe_ascii_filename = filename.encode("ascii", "ignore").decode("ascii") or "attachment"
        encoded_filename = quote(filename)
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=mime_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{safe_ascii_filename}"; '
                    f"filename*=UTF-8''{encoded_filename}"
                )
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )
