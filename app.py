import streamlit as st
import traceback
from utils.io import load_examples, load_all_transitions
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb
from utils.logger import save_output_to_file, logger
from utils.validate_prompt_compliance import validate_batch, display_validation_results
from utils.google_drive import get_google_drive_service, list_folder_contents, process_drive_files
from datetime import datetime
import pandas as pd
import io

def process_uploaded_files(uploaded_files):
    results = []
    for uploaded_file in uploaded_files:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            lines = content.strip().split('\n')
            transitions = []

            for line in lines:
                line = line.strip()
                if line.startswith("Transitions générées:"):
                    continue
                if line and line[0].isdigit() and ". " in line:
                    transition = line.split(". ", 1)[1].strip()
                    transitions.append(transition)

            if transitions:
                results.append((uploaded_file.name, transitions))

        except Exception as e:
            logger.error(f"Error processing file {uploaded_file.name}: {str(e)}")
            continue

    return results

def main():
    VERSION = compute_version_hash([
        "app.py",
        "transitions.json",
        "utils/io.py",
        "utils/processing.py",
        "utils/layout.py",
        "utils/display.py",
        "utils/version.py",
        "utils/title_blurb.py",
        "utils/logger.py"
    ])

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✨ Générer les transitions", 
        "📝 Résultat", 
        "✅ Validation",
        "💾 Sauvegarde",
        "📤 Upload par lot depuis Google Drive"
    ])

    with tab1:
        text_input = layout_title_and_input()

        if st.button("✨ Générer les transitions"):
            if "TRANSITION" not in text_input:
                st.warning("Aucune balise `TRANSITION` trouvée.")
                return
            try:
                examples = load_examples()
                logger.info("Successfully loaded examples")
                st.write("🔍 Examples preview (first 3):", examples[:3])  # ✅ DEBUG LINE

                parts = text_input.split("TRANSITION")
                pairs = list(zip(parts[:-1], parts[1:]))
                logger.info(f"Processing {len(pairs)} paragraph pairs")

                title_blurb = generate_title_and_blurb(parts[0])
                logger.info("Generated title and blurb")

                generated_transitions = []
                for i, (para_a, para_b) in enumerate(pairs, 1):
                    transition = get_transition_from_gpt(para_a, para_b, examples)
                    generated_transitions.append(transition)
                    logger.info(f"Generated transition {i}/{len(pairs)}")

                rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
                if error:
                    logger.error(f"Error rebuilding article: {error}")
                    st.error(error)
                    return

                if isinstance(title_blurb, dict):
                    st.session_state['title_text'] = title_blurb.get('title', 'Titre non défini')
                    st.session_state['chapo_text'] = title_blurb.get('chapo', 'Chapeau non défini')
                else:
                    st.session_state['title_text'] = 'Titre non défini'
                    st.session_state['chapo_text'] = 'Chapeau non défini'

                st.session_state['rebuilt_text'] = rebuilt_text
                st.session_state['generated_tr_]()_
