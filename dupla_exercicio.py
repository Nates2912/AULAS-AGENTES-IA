# ------------------------------------------------------------
# ⚔️ Criador de Personagens de D&D com IA (sem nível, ficha automática)
# ------------------------------------------------------------
import random
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from litellm.exceptions import RateLimitError

# ------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------
st.header("🎲 Criador de Personagens de D&D com IA")
st.write("Crie personagens únicos de Dungeons & Dragons com ficha completa e história geradas automaticamente!")

# Escolha de modo
modo = st.radio("Modo de criação", ["Manual", "Aleatório"])

api_key = ""  # Substitua pela sua chave Groq válida

# ------------------------------------------------------------
# ENTRADAS DO USUÁRIO
# ------------------------------------------------------------
if modo == "Manual":
    nome = st.text_input("Nome do personagem", placeholder="Ex.: Arannis Sombraluna")
    raca = st.text_input("Raça", placeholder="Ex.: Elfo, Anão, Tiefling, Humano...")
    classe = st.text_input("Classe", placeholder="Ex.: Mago, Guerreiro, Ladino, Clérigo...")
    tema = st.text_input("Tema ou conceito (opcional)", placeholder="Ex.: um mago rebelde, um paladino exilado...")
else:
    # Modo ALEATÓRIO
    racas = ["Elfo", "Anão", "Humano", "Tiefling", "Meio-Orc", "Halfling", "Draconato", "Gnomo"]
    classes = ["Mago", "Guerreiro", "Ladino", "Clérigo", "Paladino", "Bardo", "Feiticeiro", "Druida", "Patrulheiro"]
    temas = [
        "um herói relutante que foge do passado",
        "um estudioso obcecado por conhecimento proibido",
        "um mercenário em busca de redenção",
        "um aventureiro amaldiçoado por uma entidade antiga",
        "um servo leal de um deus esquecido",
        "um ladrão com coração de ouro",
        "um mago que busca dominar a morte"
    ]
    nomes = [
        "Arannis", "Thorin", "Lyra", "Kael", "Varyn", "Elara", "Dorian", "Seraphine", "Korrin", "Mira"
    ]

    nome = random.choice(nomes)
    raca = random.choice(racas)
    classe = random.choice(classes)
    tema = random.choice(temas)

    st.info(f"🧙 Personagem aleatório: **{nome}**, {raca} {classe} — {tema}")

executar = st.button("Gerar Personagem")

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
if executar:
    if not api_key:
        st.error("Por favor, insira uma API key válida antes de continuar.")
        st.stop()

    # ------------------------------------------------------------
    # MODELO DE LINGUAGEM
    # ------------------------------------------------------------
    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.7  # Mais criatividade
    )

    # ------------------------------------------------------------
    # DEFINIÇÃO DOS AGENTES
    # ------------------------------------------------------------
    agente_conceito = Agent(
        role="Criador de Conceito de Personagem de D&D",
        goal=(
            "Desenvolver o conceito do personagem {nome}, da raça {raca} e classe {classe}. "
            "Crie uma história de fundo envolvente, descreva sua personalidade, motivações e possíveis falhas. "
            "Baseie-se no tema {tema}."
        ),
        backstory=(
            "Você é um mestre de Dungeons & Dragons experiente, criativo e narrativo, "
            "especialista em criar histórias de fundo que inspiram aventuras."
        ),
        llm=llm,
        verbose=False
    )

    agente_ficha = Agent(
        role="Gerador de Ficha de D&D",
        goal=(
            "Criar a ficha técnica completa do personagem {nome}, {raca} {classe}, baseada nas regras de D&D 5e. "
            "Inclua todos os detalhes principais: atributos (FOR, DES, CON, INT, SAB, CAR), perícias, proficiências, "
            "equipamentos, magias, talentos e traços raciais. "
            "Escolha o nível e os valores automaticamente, de forma coerente com a classe e a história."
        ),
        backstory=(
            "Você é um especialista em D&D 5e que domina as mecânicas e as regras. "
            "Sabe gerar fichas completas e equilibradas com descrições claras e bem formatadas."
        ),
        llm=llm,
        verbose=False
    )

    agente_descricao = Agent(
        role="Narrador Épico de Personagens",
        goal=(
            "Apresentar o personagem {nome} de forma narrativa e imersiva. "
            "Combine história e ficha técnica em um texto épico, bem estruturado, formatado em Markdown. "
            "Organize por seções: 'Resumo', 'História', 'Ficha Técnica' e 'Gancho de Aventura'."
        ),
        backstory=(
            "Você é um bardo contador de histórias que transforma fichas em lendas. "
            "Seu estilo é cinematográfico e envolvente."
        ),
        llm=llm,
        verbose=False
    )

    # ------------------------------------------------------------
    # TAREFAS
    # ------------------------------------------------------------
    t_conceito = Task(
        description=(
            "Crie a história de fundo detalhada do personagem {nome}. "
            "Inclua origem, traços de personalidade, ideais, defeitos e objetivos. "
            "Formato: Markdown com subtítulos e listas curtas."
        ),
        agent=agente_conceito,
        expected_output="Texto em Markdown com 3–5 seções curtas."
    )

    t_ficha = Task(
        description=(
            "Monte a ficha completa do personagem {nome}, {raca} {classe}, em formato de D&D 5e. "
            "Inclua: atributos (FOR, DES, CON, INT, SAB, CAR), perícias, equipamentos, magias e talentos. "
            "Use tabelas e listas Markdown para organização."
        ),
        agent=agente_ficha,
        expected_output="Ficha técnica organizada em Markdown, com tabelas e listas."
    )

    t_descricao = Task(
        description=(
            "Combine a história e a ficha técnica e apresente o personagem {nome} "
            "em formato narrativo e visual, dividido em seções Markdown."
        ),
        agent=agente_descricao,
        expected_output="Descrição final completa do personagem em Markdown."
    )

    # ------------------------------------------------------------
    # CREW (coordenação dos agentes)
    # ------------------------------------------------------------
    crew = Crew(
        agents=[agente_conceito, agente_ficha, agente_descricao],
        tasks=[t_conceito, t_ficha, t_descricao],
        process=Process.sequential
    )

    # ------------------------------------------------------------
    # EXECUÇÃO SEGURA
    # ------------------------------------------------------------
    try:
        crew.kickoff(inputs={
            "nome": nome,
            "raca": raca,
            "classe": classe,
            "tema": tema
        })

        # Resultados
        conceito_out = getattr(t_conceito, "output", None) or getattr(t_conceito, "result", "") or ""
        ficha_out = getattr(t_ficha, "output", None) or getattr(t_ficha, "result", "") or ""
        descricao_out = getattr(t_descricao, "output", None) or getattr(t_descricao, "result", "") or ""

        # Abas de exibição
        aba_conceito, aba_ficha, aba_descricao = st.tabs(["🧙 Conceito", "📜 Ficha Técnica", "🎭 Descrição Final"])

        with aba_conceito:
            st.markdown(conceito_out)

        with aba_ficha:
            st.markdown(ficha_out)

        with aba_descricao:
            st.markdown(descricao_out)

    except RateLimitError:
        st.error("🚫 Limite de requisições atingido. Tente novamente em alguns segundos.")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
