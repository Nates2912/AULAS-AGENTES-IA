# ------------------------------------------------------------
# 📘 Agentes de IA para ensinar GML (versão com controle de erros)
# ------------------------------------------------------------
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from litellm.exceptions import RateLimitError  # Importa o tipo de erro que ocorre com limite de tokens

# ------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------
st.header("🎮 Agentes de Estudo - Linguagem GML (Game Maker Studio 2)")
st.write("Aprenda GML com agentes inteligentes que geram resumos e exemplos didáticos automaticamente!")

tema = st.text_input("Tema de estudo", placeholder="Ex.: variáveis, loops, eventos, funções")
nivel = st.text_input("Nível do público (opcional)", placeholder="Ex.: iniciante, intermediário, avançado")
objetivo = st.text_area("Objetivo (opcional)", placeholder="Ex.: entender a lógica da GML e aplicar em scripts simples")

executar = st.button("Gerar material sobre GML")

api_key = "SUA_CHAVE_API"  # Substitua pela sua chave Groq válida

if executar:
    if not api_key or not tema:
        st.error("Por favor, informe a API key e o tema de estudo.")
        st.stop()

    # ------------------------------------------------------------
    # MODELO DE LINGUAGEM
    # ------------------------------------------------------------
    # Alteramos o modelo para uma versão mais leve: "groq/llama-3.1-8b-instant"
    # Essa versão consome menos tokens e responde mais rápido.
    # ------------------------------------------------------------
    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.3
    )

    # ------------------------------------------------------------
    # DEFINIÇÃO DOS AGENTES
    # ------------------------------------------------------------
    agente_resumo = Agent(
        role="Instrutor(a) de GML",
        goal=(
            "Explicar o tema {tema} da linguagem GML de forma simples, "
            "voltada para o público {nivel}, alinhada ao objetivo {objetivo}. "
            "Deve incluir definições, usos práticos e boas práticas."
        ),
        backstory=(
            "Você é um instrutor experiente em Game Maker Studio 2 e domina GML. "
            "Explica os conceitos com clareza e exemplos práticos, "
            "voltado para iniciantes que estão aprendendo a programar jogos."
        ),
        llm=llm,
        verbose=False  # False = não mostrar logs detalhados no console
    )

    agente_exemplos = Agent(
        role="Gerador(a) de Exemplos de Código GML",
        goal=(
            "Gerar 3 exemplos práticos e curtos sobre {tema} em GML, "
            "cada um com título, descrição e código funcional. "
            "Os exemplos devem demonstrar como o conceito é usado em jogos reais."
        ),
        backstory=(
            "Você é um programador de jogos didático que mostra código GML simples "
            "e explica o que cada parte faz, contextualizando dentro de um jogo."
        ),
        llm=llm,
        verbose=False
    )

    # ------------------------------------------------------------
    # TAREFAS
    # ------------------------------------------------------------
    t_resumo = Task(
        description=(
            "Escreva um RESUMO didático sobre {tema} da linguagem GML. "
            "Inclua: definição (2–3 frases), uso prático, importância no desenvolvimento de jogos "
            "e 3–5 pontos-chave em forma de lista. "
            "Formato: Markdown com título e subtítulos."
        ),
        agent=agente_resumo,
        expected_output="Texto em Markdown com título e lista de tópicos."
    )

    t_exemplos = Task(
        description=(
            "Crie 3 exemplos práticos em GML sobre {tema}. "
            "Cada exemplo deve ter: **título**, breve descrição e código GML formatado. "
            "Mostre o código entre blocos Markdown com ```gml```."
        ),
        agent=agente_exemplos,
        expected_output="Lista numerada (1–3) com exemplos curtos, cada um com explicação e código."
    )

    # ------------------------------------------------------------
    # CREW (Orquestração dos agentes)
    # ------------------------------------------------------------
    crew = Crew(
        agents=[agente_resumo, agente_exemplos],
        tasks=[t_resumo, t_exemplos],
        process=Process.sequential
    )

    # ------------------------------------------------------------
    # EXECUÇÃO SEGURA (com tratamento de RateLimitError)
    # ------------------------------------------------------------
    try:
        # Tenta rodar o processo normalmente
        crew.kickoff(inputs={
            "tema": tema,
            "nivel": nivel or "não informado",
            "objetivo": objetivo or "não informado",
        })

        # Coleta as saídas de cada tarefa
        resumo_out = getattr(t_resumo, "output", None) or getattr(t_resumo, "result", "") or ""
        exemplos_out = getattr(t_exemplos, "output", None) or getattr(t_exemplos, "result", "") or ""

        # Mostra as abas no Streamlit
        aba_resumo, aba_exemplos = st.tabs(["Resumo", "Exemplos"])

        with aba_resumo:
            st.markdown(resumo_out)

        with aba_exemplos:
            st.markdown(exemplos_out)

    except RateLimitError as e:
        # Se o limite de tokens for atingido, exibe mensagem amigável
        st.error("🚫 Limite de requisições da API atingido. Tente novamente em alguns segundos.")
        st.info("Dica: use um modelo menor ou aguarde 5–10 segundos antes de tentar novamente.")

    except Exception as e:
        # Captura qualquer outro erro inesperado
        st.error(f"Ocorreu um erro inesperado: {e}")
