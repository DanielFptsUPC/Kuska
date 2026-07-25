import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# Confirmado contra la API real: modelos disponibles son gemma-4-31b-it y gemma-4-26b-a4b-it (mas rapido, MoE).
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-31b-it")

PROMPT_TEMPLATE = """Eres un sistema de apoyo a la respuesta ante desastres. Analiza la(s) foto(s)/video y la
descripcion del ciudadano. Responde SOLO un JSON con este esquema exacto, sin texto adicional:
{{
  "type": "colapso_estructural | grietas | incendio | persona_atrapada | via_bloqueada | otro",
  "damage_level": "leve | moderado | severo | critico",
  "trapped_people_possible": true | false,
  "secondary_risks": ["fuego", "gas", "cables_electricos"],
  "priority": "alta | media | baja",
  "explanation": "1-2 frases explicando el razonamiento, en espanol"
}}
Descripcion del ciudadano: "{description}"
"""

FALLBACK_RESULT = {
    "type": "otro",
    "damage_level": "moderado",
    "trapped_people_possible": False,
    "secondary_risks": [],
    "priority": "media",
    "explanation": "No se pudo clasificar automaticamente; requiere revision manual.",
}


def classify_incident(photo_bytes_list: list[bytes], description: str) -> dict:
    parts = [types.Part.from_text(text=PROMPT_TEMPLATE.format(description=description))]
    for photo_bytes in photo_bytes_list:
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg"))

    response = client.models.generate_content(model=GEMMA_MODEL, contents=parts)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[len("json"):]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return FALLBACK_RESULT
