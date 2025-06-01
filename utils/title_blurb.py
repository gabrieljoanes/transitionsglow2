# utils/title_blurb.py

import requests
import streamlit as st

# Load API credentials from Streamlit secrets
API_TOKEN = st.secrets.get("API_TOKEN")
API_URL = st.secrets.get("API_URL")

if not API_TOKEN:
    raise ValueError("API_TOKEN is not set in Streamlit secrets")

PROMPT = """Tu es un assistant de rédaction pour un journal local français.

Ta tâche est de générer un **titre** et un **chapeau** (blurb) à partir du **premier paragraphe uniquement**.

Règles :

1. Titre :
   - Court, clair et journalistique (max. 12 mots).
   - Inclure le lieu si mentionné dans le paragraphe.
   - Inclure la date si mentionnée dans le paragraphe.
   - Doit annoncer le fait principal.

2. Chapeau :
   - Résume quoi, qui, où, quand.
   - Mentionner la date et le lieu s'ils sont dans le paragraphe.
   - Max. 30 mots, ton neutre.

Utilise uniquement le contenu du paragraphe fourni, sans rien ajouter.

Format de réponse :
Titre : [titre généré]
Chapeau : [chapeau généré]
"""

def generate_title_and_blurb(paragraph: str) -> dict:
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": paragraph.strip()}
        ],
        "temperature": 0.5,
        "max_tokens": 150
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    response_data = response.json()

    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise Exception("Unexpected API response format")

    # Parse title and chapeau
    title = ""
    chapo = ""
    for line in content.splitlines():
        if line.lower().startswith("titre :"):
            title = line.split(":", 1)[1].strip()
        elif line.lower().startswith("chapeau :"):
            chapo = line.split(":", 1)[1].strip()

    return {
        "title": title or "Titre non défini",
        "chapo": chapo or "Chapeau non défini"
    }
