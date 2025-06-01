    with tab1:
        text_input = layout_title_and_input()

        if st.button("✨ Générer les transitions"):
            if "TRANSITION" not in text_input:
                st.warning("Aucune balise `TRANSITION` trouvée.")
                return
            try:
                examples = load_examples()
                logger.info("Successfully loaded examples")
                st.write("🔍 Examples preview (first 3):", examples[:3])  # ✅ DEBUG

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
                st.session_state['generated_transitions'] = generated_transitions

            except Exception:
                st.error("🚨 Une erreur est survenue lors de la génération.")
                st.code(traceback.format_exc(), language="python")
                logger.error(traceback.format_exc())
