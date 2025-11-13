# ------------------------------------------------------------
# 🧙 Agentes de IA para Criação de Personagens de D&D
# ------------------------------------------------------------
import os
import time
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from litellm.exceptions import RateLimitError

# ------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------
st.header("🧙‍♂️ Gerador de Personagens de Dungeons & Dragons (IA)")
st.write("Crie automaticamente fichas de personagem completas com história, atributos e descrição física!")

# Campos básicos
nome = st.text_input("Nome do personagem", placeholder="Ex.: Thalindra Sombrasol")
raca = st.text_input("Raça", placeholder="Ex.: Elfo, Anão, Tiefling, etc.")
classe = st.text_input("Classe", placeholder="Ex.: Mago, Guerreiro, Ladino, etc.")
tema = st.text_area("Tema ou estilo (opcional)", placeholder="Ex.: sombrio, cômico, trágico, aventureiro...")

executar = st.button("🎲 Gerar Personagem")

api_key = ""  # Substitua pela sua API key válida (Groq ou OpenAI)

# ------------------------------------------------------------
# FUNÇÃO DE EXECUÇÃO SEGURA COM RE-TENTATIVA
# ------------------------------------------------------------
def tentar_executar(crew, inputs, tentativas=3, espera=5):
    """
    Executa o Crew com tratamento de erros e re-tentativas automáticas.
    - crew: objeto Crew()
    - inputs: dicionário de variáveis para o processo
    - tentativas: número máximo de tentativas antes de desistir
    - espera: segundos entre tentativas em caso de erro
    """
    for i in range(tentativas):
        try:
            st.info(f"🧠 Gerando personagem... (Tentativa {i+1}/{tentativas})")
            resultado = crew.kickoff(inputs=inputs)
            return resultado
        except RateLimitError:
            if i < tentativas - 1:
                st.warning(f"🚦 Limite atingido. Tentando novamente em {espera} segundos...")
                time.sleep(espera)
            else:
                st.error("🚫 Falha após várias tentativas. Tente novamente mais tarde.")
                return None
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            return None

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
if executar:
    if not api_key or not nome or not raca or not classe:
        st.error("Por favor, preencha o nome, raça, classe e informe a API key.")
        st.stop()

    # ------------------------------------------------------------
    # CONFIGURAÇÃO DO MODELO DE LINGUAGEM
    # ------------------------------------------------------------
    llm = LLM(
        model="groq/llama-3.1-8b-instant",  # Pode trocar por "gpt-4o-mini"
        api_key=api_key,
        temperature=0.7
    )

    # ------------------------------------------------------------
    # DEFINIÇÃO DOS AGENTES
    # ------------------------------------------------------------
    agente_conceito = Agent(
        role="Criador de Conceito de Personagem",
        goal=(
            "Criar um conceito único e interessante para um personagem de D&D "
            "chamado {nome}, que é da raça {raca} e classe {classe}. "
            "Deve descrever sua personalidade, motivações e um breve resumo da história."
        ),
        backstory=(
            "Você é um mestre de RPG criativo que entende o equilíbrio entre narrativa e jogabilidade. "
            "Seu trabalho é criar personagens cativantes e coerentes com o universo de D&D."
        ),
        llm=llm,
        verbose=False
    )

    agente_ficha = Agent(
        role="Construtor de Ficha de Personagem",
        goal=(
            "Gerar uma ficha básica de D&D 5e para o personagem {nome}, "
            "incluindo atributos (FOR, DES, CON, INT, SAB, CAR), alinhamento, "
            "equipamentos iniciais e habilidades de classe."
        ),
        backstory=(
            "Você é um especialista em regras de D&D 5e e entende como montar fichas equilibradas "
            "para personagens de qualquer nível e classe."
        ),
        llm=llm,
        verbose=False
    )

    agente_descricao = Agent(
        role="Descritor Artístico",
        goal=(
            "Gerar uma descrição física e visual do personagem {nome}, "
            "incluindo aparência, vestimentas, expressões e estilo de fala. "
            "O texto deve ser descritivo e inspirar arte conceitual."
        ),
        backstory=(
            "Você é um ilustrador de fantasia acostumado a transformar palavras em imagens vívidas. "
            "Você descreve personagens de forma que o leitor visualize claramente cada detalhe."
        ),
        llm=llm,
        verbose=False
    )

    # ------------------------------------------------------------
    # TAREFAS
    # ------------------------------------------------------------
    t_conceito = Task(
        description="Crie o CONCEITO do personagem {nome} ({raca}, {classe}).",
        agent=agente_conceito,
        expected_output="Texto de 2 a 3 parágrafos descrevendo conceito e história."
    )

    t_ficha = Task(
        description="Monte a FICHA de D&D 5e para {nome}, com atributos e informações básicas.",
        agent=agente_ficha,
        expected_output="Ficha de personagem em Markdown, com tabela de atributos e seções nomeadas."
    )

    t_descricao = Task(
        description="Crie uma DESCRIÇÃO física e visual detalhada do personagem {nome}.",
        agent=agente_descricao,
        expected_output="Texto descritivo em tom literário curto (1-2 parágrafos)."
    )

    # ------------------------------------------------------------
    # ORGANIZAÇÃO DOS AGENTES (CREW)
    # ------------------------------------------------------------
    crew = Crew(
        agents=[agente_conceito, agente_ficha, agente_descricao],
        tasks=[t_conceito, t_ficha, t_descricao],
        process=Process.sequential
    )

    # ------------------------------------------------------------
    # EXECUÇÃO COM SEGURANÇA E RETENTATIVA
    # ------------------------------------------------------------
    resultado = tentar_executar(crew, {
        "nome": nome,
        "raca": raca,
        "classe": classe,
        "tema": tema or "não especificado"
    })

    if resultado:
        # Pausas pequenas para evitar rate limit durante leitura
        time.sleep(2)
        conceito_out = getattr(t_conceito, "output", "") or getattr(t_conceito, "result", "")
        time.sleep(2)
        ficha_out = getattr(t_ficha, "output", "") or getattr(t_ficha, "result", "")
        time.sleep(2)
        descricao_out = getattr(t_descricao, "output", "") or getattr(t_descricao, "result", "")

        # Exibição organizada
        aba1, aba2, aba3 = st.tabs(["🧩 Conceito", "📜 Ficha", "🎨 Descrição"])

        with aba1:
            st.markdown(conceito_out)

        with aba2:
            st.markdown(ficha_out)

        with aba3:
            st.markdown(descricao_out)
