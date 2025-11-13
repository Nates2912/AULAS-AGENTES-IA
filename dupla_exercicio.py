# ------------------------------------------------------------
# ⚔️ Agentes de IA para Criação de Personagens de D&D (com modo aleatório)
# ------------------------------------------------------------
import os
import random
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from litellm.exceptions import RateLimitError

# ------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------
st.header("🎲 Criador de Personagens de D&D com IA")
st.write("Crie personagens únicos de Dungeons & Dragons com ajuda de agentes inteligentes!")

# Escolha de modo
modo = st.radio("Modo de criação", ["Manual", "Aleatório"])

api_key = ""  # Coloque sua chave Groq aqui

# ------------------------------------------------------------
# ENTRADAS DO USUÁRIO
# ------------------------------------------------------------
if modo == "Manual":
    nome = st.text_input("Nome do personagem", placeholder="Ex.: Arannis Sombraluna")
    raca = st.text_input("Raça", placeholder="Ex.: Elfo, Anão, Tiefling, Humano...")
    classe = st.text_input("Classe", placeholder="Ex.: Mago, Guerreiro, Ladino, Clérigo...")
    nivel = st.number_input("Nível", min_value=1, max_value=20, value=1)
    tema = st.text_input("Tema ou conceito (opcional)", placeholder="Ex.: um mago rebelde, um paladino exilado...")
else:
    # GERAÇÃO ALEATÓRIA SIMPLES
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

    # Escolha aleatória de atributos
    nome = random.choice(nomes)
    raca = random.choice(racas)
    classe = random.choice(classes)
    nivel = random.randint(1, 10)
    tema = random.choice(temas)

    st.info(f"🧙 Personagem aleatório: **{nome}**, {raca} {classe} (nível {nivel}) — {tema}")

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
        temperature=0.7  # Um pouco mais criativo para gerar histórias únicas
    )

    # ------------------------------------------------------------
    # AGENTES
    # ------------------------------------------------------------
    agente_conceito = Agent(
        role="Criador de Conceito de Personagem",
        goal=(
            "Desenvolver o conceito do personagem {nome}, da raça {raca}, classe {classe} e nível {nivel}. "
            "Gerar uma história de fundo envolvente e uma personalidade coerente com o tema {tema}."
        ),
        backstory=(
            "Você é um mestre de D&D apaixonado por criar personagens interessantes. "
            "Gosta de misturar drama, mistério e humor nas histórias de fundo."
        ),
        llm=llm,
        verbose=False
    )

    agente_ficha = Agent(
        role="Gerador de Ficha Técnica de D&D",
        goal=(
            "Montar a ficha técnica do personagem {nome} com base nas regras de D&D 5e. "
            "Incluir atributos, perícias, equipamentos, magias e traços raciais. "
            "Os valores devem ser equilibrados e condizentes com o nível {nivel}."
        ),
        backstory=(
            "Você é um especialista em D&D 5e e conhece todas as classes, magias e raças. "
            "Gera fichas equilibradas e coerentes com a narrativa."
        ),
        llm=llm,
        verbose=False
    )

    agente_descricao = Agent(
        role="Narrador Épico de Personagens",
        goal=(
            "Apresentar o personagem {nome} de forma cinematográfica, unindo história e ficha técnica. "
            "Usar formatação em Markdown, com seções, títulos e listas bem estruturadas."
        ),
        backstory=(
            "Você é um bardo e narrador que transforma fichas de personagem em lendas. "
            "Sua escrita é vívida, imersiva e com um toque poético."
        ),
        llm=llm,
        verbose=False
    )

    # ------------------------------------------------------------
    # TAREFAS
    # ------------------------------------------------------------
    t_conceito = Task(
        description=(
            "Crie a história de fundo do personagem {nome}. "
            "Inclua origem, traços de personalidade, objetivos e conflitos internos. "
            "Formato: Markdown com seções curtas ('História', 'Personalidade', 'Motivações')."
        ),
        agent=agente_conceito,
        expected_output="História curta em Markdown organizada em seções."
    )

    t_ficha = Task(
        description=(
            "Monte uma ficha técnica de D&D 5e para {nome}. "
            "Inclua: Atributos (FOR, DES, CON, INT, SAB, CAR), perícias, equipamentos e magias principais. "
            "Apresente em formato de tabela e listas Markdown."
        ),
        agent=agente_ficha,
        expected_output="Ficha técnica completa em Markdown."
    )

    t_descricao = Task(
        description=(
            "Combine a história e a ficha técnica para criar uma apresentação final épica do personagem {nome}. "
            "Organize com títulos, subtítulos e listas Markdown bem formatadas."
        ),
        agent=agente_descricao,
        expected_output="Descrição narrativa completa do personagem em Markdown."
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
            "nivel": nivel,
            "tema": tema
        })

        # Resultados
        conceito_out = getattr(t_conceito, "output", None) or getattr(t_conceito, "result", "") or ""
        ficha_out = getattr(t_ficha, "output", None) or getattr(t_ficha, "result", "") or ""
        descricao_out = getattr(t_descricao, "output", None) or getattr(t_descricao, "result", "") or ""

        # Exibição
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
