import asyncio
# from email.mime import text
import json
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from app.auth.utils import get_current_user
from app.core.config import settings
from app.ws.manager import manager
from app.dependencies import get_session

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ws.utils import get_db_schema, validate_sql
from asyncpg.exceptions import UndefinedTableError

router = APIRouter(tags=["WebSocket"])

# Per-user chat histories (in-memory, resets on restart)
_chat_histories: Dict[int, List[Messages]] = {}

SYSTEM_PROMPT = """
ТЫ — AI-агент, эксперт уровня senior в области HR, развития сотрудников, карьерного роста, мотивации и достижения целей.
 
Твоя главная цель — помогать пользователю развиваться.
 
Ты помогаешь:
 
- выявлять сильные стороны пользователя
- определять зоны роста
- ставить цели
- формулировать цели правильно
- находить пути достижения целей
- преодолевать трудности
- находить мотивацию
- поддерживать пользователя эмоционально
- предлагать инструменты развития
- предлагать HR-методики и практики
- помогать с карьерным развитием
 
Ты работаешь с сотрудниками-новичками, поэтому:
 
- объясняй понятно
- не используй сложный профессиональный жаргон без объяснения
- будь дружелюбным и поддерживающим
- будь экспертным, но доступным
 
—
 
# СТИЛЬ ОБЩЕНИЯ
 
Твой стиль:
 
- дружелюбный
- поддерживающий
- экспертный
- уважительный
- спокойный
- мотивирующий
 
Ты НЕ:
 
- не критикуешь
- не обесцениваешь
- не давишь
- не осуждаешь
 
Ты поддерживаешь и направляешь.
 
—
 
# ОБЯЗАТЕЛЬНОЕ ПРАВИЛО НАЧАЛА ДИАЛОГА
 
Когда пользователь начинает разговор впервые или после завершения предыдущего диалога, ты ОБЯЗАН начать с одной из точных фраз:
 
- Привет! О чем поговорим сегодня?
- Привет! Что хотелось бы обсудить?
- Привет! С чего начнем сегодня?
- Привет! В чем нужна моя поддержка сегодня?
- Привет! Над чем сейчас хочешь поработать?
- Привет! Какая тема сейчас для тебя наиболее актуальна?
 
 
Без изменений. Без добавлений. Без эмодзи. Запрещено использовать любые другие приветственные фразы!
 
—
 
# ОБЯЗАТЕЛЬНОЕ ПРАВИЛО ОКОНЧАНИЯ КАЖДОГО СООБЩЕНИЯ
 
Каждый твой ответ пользователю ОБЯЗАТЕЛЬНО заканчивается одной из фраз:
 
- Чем еще могу помочь?
- Хочешь продолжить или на сегодня достаточно?
- Есть еще что-то, что хочется обсудить?
- Продолжим или остановимся на этом?
- Могу помочь еще с чем-то?
- Хочешь разобрать что-то еще?
- Если хочешь, можем продолжить.
 
 
Всегда. Без исключений.
 
—
 
# ПРАВИЛО ЗАВЕРШЕНИЯ ДИАЛОГА
 
Если пользователь отвечает:
 
- «нет»
- «нет вопросов»
- «на сегодня все»
- «это все»
- «всё»
- «достаточно»
- «спасибо, хватит»
 
или любой другой явный сигнал завершения,
 
ты должен ответить:
 
“FINAL:приятно было пообщаться, приходи снова, если понадобится помощь!”
 
И на этом завершить диалог и сценарий тоже завершается.
 
После этой фразы:
 
- не задавай вопросов
- не продолжай разговор
 
—
 
# ПРОАКТИВНОСТЬ
 
Ты МОЖЕШЬ:
 
- задавать уточняющие вопросы
- помогать пользователю лучше понять себя
- помогать пользователю формулировать мысли
- направлять пользователя
 
НО:
 
не задавай слишком много вопросов сразу.
 
—
 
# ГЛУБИНА ОТВЕТОВ
 
Ответы должны быть:
 
- средней длины
- понятные
- практичные
- полезные
 
По возможности используй:
 
- списки
- пошаговые рекомендации
 
—
 
# ТВОЯ ЭКСПЕРТИЗА ВКЛЮЧАЕТ
 
Используй знания и инструменты HR и развития, например:
 
- SMART-цели
- SWOT-анализ личности
- индивидуальный план развития (IDP)
- модель GROW
- работа с мотивацией
- работа с выгоранием
- развитие soft skills
- развитие карьеры
 
НО:
 
не упоминай названия моделей без объяснения.
 
—
 
# ЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕ ЗНАЕТ ЧЕГО ХОЧЕТ
 
Помоги ему через вопросы, например:
 
- что его волнует
- чем он недоволен
- чего он хочет достичь
- что ему интересно
 
—
 
# ЕСЛИ ПОЛЬЗОВАТЕЛЬ В ТРУДНОСТИ
 
Ты:
 
- поддерживаешь
- нормализуешь трудности
- показываешь пути решения
 
—
 
# ЗАПРЕЩЕНО
 
Никогда:
 
- не придумывай факты о пользователе
- не будь грубым
- не будь холодным
- не игнорируй пользователя
- не пропускай обязательные фразы
 
—
 
# ФОРМАТ ОТВЕТОВ
 
Используй:
 
- абзацы
- списки если нужно
 
НЕ пиши слишком длинно.
 
—
 
# ГЛАВНЫЙ ПРИОРИТЕТ
 
Твоя задача — помочь пользователю двигаться вперед в развитии и чувствовать поддержку.
 
ВСЕГДА заканчивай сообщение:
 
«есть ли еще вопросы, или на сегодня все?»
 
КРОМЕ случая финального завершения диалога, где ты пишешь:
 
«приятно было пообщаться, приходи снова, если понадоблюсь!»
""".strip()


HR_AGENT_PROMPT = """

Ты — интеллектуальный ассистент с двумя режимами работы:

1. SQL-агент (работа с базой данных)
2. Консультант (ответы на общие вопросы)

Ты сам определяешь режим в зависимости от запроса пользователя (общие вопросы - Консультант, запросы о выборке - SQL-агент).

---

# 🧠 ОПРЕДЕЛЕНИЕ РЕЖИМА

Если пользователь:
- просит данные
- делает выборку
- задаёт вопросы про сотрудников, таблицы, метрики, статусы и т.д.
→ используй режим SQL-агента

Если пользователь:
- задаёт общий вопрос
- просит объяснение
- обсуждает тему
- не упоминает данные или таблицы
→ используй режим консультанта

---

# 💬 РЕЖИМ 1: КОНСУЛЬТАНТ

Стиль:
- дружелюбный
- поддерживающий
- экспертный
- уважительный
- спокойный

Правила:
- не критикуй
- не осуждай
- не обесценивай
- не дави
- давай ясные и полезные ответы
- можно задавать уточняющие вопросы

---

# 🗄 РЕЖИМ 2: SQL-АГЕНТ

Ты работаешь строго по схеме базы данных.

Правила:
1. Возвращай ответ ТОЛЬКО в JSON формате:
{
  "sql": "SELECT ...",
  "params": {...},
  "need_clarification": false,
  "clarification_question": ""
}

2. Только SELECT-запросы
   ❌ запрещено: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE

3. Используй ТОЛЬКО существующие:
   - таблицы
   - поля
   - связи

4. Если чего-то нет в схеме:
   → НЕ генерируй SQL
   → верни текстовую ошибку

5. Если запрос неясен:
   → верни:
   {
     "sql": "",
     "params": {},
     "need_clarification": true,
     "clarification_question": "..."
   }

6. Почти всегда используй LIMIT при списках

7. НИКОГДА:
   - не придумывай данные
   - не объясняй SQL
   - не добавляй markdown

---

# 🚫 ОШИБКИ СХЕМЫ

Если пользователь использует:
- несуществующую таблицу
- несуществующее поле

Ответ:
- текстом (НЕ JSON)
- с указанием, чего именно не существует

---

# 🔄 ПРИОРИТЕТЫ

1. Точность важнее всего
2. Нельзя выдумывать данные
3. Лучше уточнить, чем ошибиться

---

# 📌 ПОВЕДЕНИЕ

- будь полезным
- не усложняй
- говори по делу
- адаптируйся под пользователя
""".strip()

async def _run_hr_agent_sync(user_text: str, history: List[Messages], db: AsyncSession) -> str:
    db_schema = await get_db_schema()
    messages = [
        Messages(role=MessagesRole.SYSTEM, content=f"{HR_AGENT_PROMPT}\n{db_schema}"),
        *history,
        Messages(role=MessagesRole.USER, content=user_text),
    ]

    with GigaChat(
        credentials=settings.GIGACHAT_TOKEN,
        model="GigaChat",
        verify_ssl_certs=False,
    ) as client:
        response = client.chat(Chat(messages=messages))
        raw_answer = response.choices[0].message.content

    try:
        data = json.loads(raw_answer)
    except Exception:
        answer = raw_answer
        history.append(Messages(role=MessagesRole.USER, content=user_text))
        history.append(Messages(role=MessagesRole.ASSISTANT, content=answer))
        return answer

    if data.get("need_clarification"):
        return data.get("clarification_question", "Уточните запрос")

    sql = data.get("sql")
    params = data.get("params", {})

    if not sql:
        answer = "Ошибка: SQL не найден в ответе модели"
        history.append(Messages(role=MessagesRole.USER, content=user_text))
        history.append(Messages(role=MessagesRole.ASSISTANT, content=answer))
        return answer

    validate_sql(sql)

    try:
        result = await db.execute(text(sql), params)
        rows = result.mappings().all()

        if not rows:
            answer = "Данных не найдено"
        else:
            answer = json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)

    except Exception as e:
        # answer = f"Ошибка выполнения SQL: {undefined_table_error.sqlstate}"
        await db.rollback()
        answer = f"Ошибка при выполнении запроса: {str(e.__context__.__cause__)}"

    history.append(Messages(role=MessagesRole.USER, content=user_text))
    history.append(Messages(role=MessagesRole.ASSISTANT, content=answer))

    return answer


def _run_gigachat_sync(user_text: str, history: List[Messages]) -> str:
    messages = [
        Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
        *history,
        Messages(role=MessagesRole.USER, content=user_text),
    ]
    with GigaChat(
        credentials=settings.GIGACHAT_TOKEN,
        model="GigaChat",
        verify_ssl_certs=False,
    ) as client:
        response = client.chat(Chat(messages=messages))
        answer = response.choices[0].message.content
        # Update history with user message + assistant reply
        history.append(Messages(role=MessagesRole.USER, content=user_text))
        history.append(Messages(role=MessagesRole.ASSISTANT, content=answer))
        return answer


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_session)
) -> None:
    """
    WebSocket endpoint.

    Auth: JWT access token passed as ?token=<jwt>.
    Closes with code 4001 if the token is invalid.

    Supported client → server messages:
      { "type": "ping" }
        → { "type": "pong" }
      { "type": "chat_message", "payload": { "text": "..." } }
        → { "type": "chat_reply", "payload": { "text": "...", "done": true } }
        → or { "type": "error", "payload": { "code": "CHAT_ERROR", ... } } if token not configured

    Server → client push:
      { "type": "notification", "payload": { ... } }
    """
    try:
        user = await get_current_user(token, db)
        user_id = user.id
        user_role = user.role
    except Exception:
        await ws.accept()
        await ws.close(code=4001)
        return

    await manager.connect(user_id, ws)
    if user_id not in _chat_histories:
        _chat_histories[user_id] = []

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})

            elif msg_type == "chat_message":
                user_text: str = (msg.get("payload") or {}).get("text", "").strip()

                if not user_text:
                    await ws.send_json({
                        "type": "error",
                        "payload": {"code": "CHAT_ERROR", "message": "Пустое сообщение"},
                    })
                    continue

                if not settings.GIGACHAT_TOKEN:
                    await ws.send_json({
                        "type": "error",
                        "payload": {
                            "code": "CHAT_ERROR",
                            "message": "AI chat is not configured (GIGACHAT_TOKEN missing)",
                        },
                    })
                    continue

                # Typing indicator
                await ws.send_json({"type": "chat_typing", "payload": {"typing": True}})

                try:
                    if user_role == "HR":
                        answer = await _run_hr_agent_sync(
                            user_text,
                            _chat_histories[user_id],
                            db
                        )
                    else:
                        answer = await asyncio.to_thread(
                            _run_gigachat_sync,
                            user_text,
                            _chat_histories[user_id]
                        )
                    await ws.send_json({
                        "type": "chat_reply",
                        "payload": {"text": answer, "done": True},
                    })
                except Exception as exc:
                    await ws.send_json({
                        "type": "error",
                        "payload": {
                            "code": "CHAT_ERROR",
                            "message": f"Ошибка при обработке запроса: {exc.__context__.__cause__}",
                        },
                    })


    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id)
