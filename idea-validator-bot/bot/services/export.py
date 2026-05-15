import json
import os
from datetime import datetime

from bot.services.validator import get_verdict, WEIGHT_VALUES


async def generate_txt(idea_title: str, pros: list, cons: list) -> str:
    verdict = get_verdict(pros, cons)
    pro_lines = [f"+ [{a.weight}] {a.text}" for a in pros]
    con_lines = [f"- [{a.weight}] {a.text}" for a in cons]

    pro_text = '\n'.join(pro_lines) if pro_lines else '(нет)'
    con_text = '\n'.join(con_lines) if con_lines else '(нет)'

    content = (
        f"Валидация идеи: \"{idea_title}\"\n"
        f"Вердикт: {verdict.text}\n"
        f"Score: {verdict.score}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"ПОДТВЕРЖДАЕТ БОЛЬ:\n"
        f"{pro_text}\n\n"
        f"ЛОМАЕТ ИДЕЮ:\n"
        f"{con_text}"
    )
    return content


async def generate_json(idea_title: str, pros: list, cons: list) -> str:
    verdict = get_verdict(pros, cons)
    data = {
        "idea": idea_title,
        "arguments": {
            "pro": [{"text": a.text, "weight": a.weight} for a in pros],
            "con": [{"text": a.text, "weight": a.weight} for a in cons],
        },
        "verdict": {
            "text": verdict.text,
            "score": verdict.score,
            "key": verdict.key,
            "confidence": verdict.confidence,
        },
        "exportedAt": datetime.now().isoformat(),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


async def save_to_file(content: str, filename: str) -> str:
    data_dir = "data/exports"
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
