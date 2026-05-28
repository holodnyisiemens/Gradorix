from typing import Any

from sqlalchemy import inspect
import inspect as py_inspect
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.database import async_engine
from app.core import enums as enums_module
from app.core.enums import ReportFileFormat
from enum import Enum
from pathlib import Path
from uuid import uuid4
import pandas as pd
from xhtml2pdf import pisa


REPORTS_DIR = Path("reports")


def _ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    return REPORTS_DIR


def normalize_report_filename(filename: str | None, report_format: str) -> str:
    stem = Path((filename or "report").strip() or "report").stem
    ext = ".pdf" if report_format == ReportFileFormat.PDF else ".xlsx"
    return f"{stem}{ext}"


def generate_excel(rows, filename: str = "report.xlsx") -> tuple[str, str]:
    """
    Returns:
        saved_filename, full_path
    """
    reports_dir = _ensure_reports_dir()

    saved_filename = f"{uuid4().hex}_{filename}"
    full_path = reports_dir / saved_filename

    df = pd.DataFrame([dict(row) for row in rows])
    df.to_excel(full_path, index=False)

    return saved_filename, str(full_path)


def generate_pdf(rows, filename: str = "report.pdf") -> tuple[str, str]:
    """
    Returns:
        saved_filename, full_path
    """
    reports_dir = _ensure_reports_dir()

    saved_filename = f"{uuid4().hex}_{filename}"
    full_path = reports_dir / saved_filename

    df = pd.DataFrame([dict(row) for row in rows])
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
  body {{ font-family: DejaVu Sans, Arial, sans-serif; font-size: 10px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 4px 6px; text-align: left; }}
  th {{ background: #f0f0f0; }}
</style></head>
<body>{df.to_html(index=False, escape=True)}</body>
</html>"""

    with open(full_path, "wb") as pdf_file:
        status = pisa.CreatePDF(html, dest=pdf_file, encoding="utf-8")
        if status.err:
            raise RuntimeError("Не удалось сформировать PDF-отчёт")

    return saved_filename, str(full_path)


def generate_report_file(
    rows,
    filename: str,
    report_format: str,
) -> tuple[str, str]:
    if report_format == ReportFileFormat.PDF:
        return generate_pdf(rows, filename)
    return generate_excel(rows, filename)



def collect_enums() -> dict:
    enums_dict = {}

    for name, obj in py_inspect.getmembers(enums_module):
        if isinstance(obj, type) and issubclass(obj, Enum):
            enums_dict[name] = [e.value for e in obj]

    return enums_dict


async def dump_schema(async_engine: AsyncEngine, schema: str | None = "public") -> dict[str, Any]:
    def _load(sync_conn):
        insp = inspect(sync_conn)

        tables: dict[str, Any] = {}
        for table_name in insp.get_table_names(schema=schema):
            tables[table_name] = {
                "columns": insp.get_columns(table_name, schema=schema),
                "primary_key": insp.get_pk_constraint(table_name, schema=schema),
                "foreign_keys": insp.get_foreign_keys(table_name, schema=schema),
                "indexes": insp.get_indexes(table_name, schema=schema),
            }

        return {"schema": schema, "tables": tables}

    async with async_engine.connect() as conn:
        return await conn.run_sync(_load)
    

async def get_db_schema() -> str:

    res = {
        "schema": None,
        "relations": [],
        "enums": None,
    }

    schema = await dump_schema(async_engine, "public")
    res["schema"] = schema

    for table, data in schema["tables"].items():
        res[table] = [col["name"] for col in data["columns"]]

    res["enums"] = collect_enums()

    return f"Схема таблиц: {res['schema']}\nСвязи между таблицами: {res['relations']}\nПеречисление ENUMов: {res['enums']}"



def validate_sql(sql: str):
    sql_lower = sql.strip().lower()

    if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
        raise ValueError("Разрешены только SELECT-запросы")

    if ";" in sql_lower.strip(";"):
        raise ValueError("Только один SQL-запрос")

    forbidden = [
        "insert", "update", "delete", "drop",
        "alter", "create", "truncate"
    ]
    for word in forbidden:
        if word in sql_lower:
            raise ValueError(f"Запрещено использовать {word.upper()}")
            
