from typing import Any

from sqlalchemy import inspect
import inspect as py_inspect
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.database import async_engine
from app.core import enums as enums_module
from enum import Enum


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
            
