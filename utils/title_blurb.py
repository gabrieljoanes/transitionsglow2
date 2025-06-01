import requests
import streamlit as st

API_TOKEN = st.secrets.get("API_TOKEN")
API_URL = st.secrets.get("API_URL")

if not API_TOKEN:
    raise ValueError("API_TOKEN secret is not set")

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

def generate_title_and_blurb(paragraph):
    # Construct full prompt
    full_prompt = f"{PROMPT}\n\n{paragraph.strip()}"

    # Log prompt for debugging
    st.write("🧪 Prompt sent to API:")
    st.code(full_prompt, language="markdown")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": full_prompt
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
    except Exception as e:
        st.error("🚨 Erreur lors de l'appel à l'API")
        st.code(str(e))
        raise

    # Log raw response for debugging
    st.write("🧪 Raw API response:")
    st.code(response.text)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    response_data = response.json()
    if response_data.get("status") != "success":
        raise Exception(f"API error: {response_data.get('error', 'Unknown error')}")

    return response_data["reply"].strip()
