import os
import re
import time
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from litellm.exceptions import RateLimitError

# ---------------------------
# Configuração de página
# ---------------------------
st.set_page_config(page_title="Tutor GML com IA", page_icon="🎮", layout="centered")

st.title("🎮 Tutor GML com IA — Aprenda passo a passo")
st.write("Aprenda GML com teoria, exemplos e mini-projetos — e continue cada tema do ponto em que parou!")

# ---------------------------
# Entrada do usuário
# ---------------------------
tema = st.text_input("Tópico GML", placeholder="Ex.: variáveis, eventos, scripts, colisões, arrays")
nivel = st.text_input("Nível (opcional)", placeholder="Ex.: iniciante, intermediário, avançado")
objetivo = st.text_area("Objetivo (opcional)", placeholder="Ex.: entender como usar variáveis e estruturas de controle no GML")

executar = st.button("Iniciar / Continuar tutorial")
api_key = 'SUA_CHAVE_API'  # ← coloque sua chave do Groq aqui

# ---------------------------
# Funções de salvamento
# ---------------------------
def nome_arquivo(tema):
    base = re.sub(r'[^a-zA-Z0-9_-]+', '_', tema.strip().lower())
    return f"progresso_{base}.txt"

def salvar_progresso(tema, passo):
    if not tema:
        return
    with open(nome_arquivo(tema), "w") as f:
        f.write(str(passo))

def carregar_progresso(tema):
    if not tema:
        return 1
    arquivo = nome_arquivo(tema)
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 1
    return 1

# ---------------------------
# Estado inicial
# ---------------------------
if "passo" not in st.session_state:
    st.session_state.passo = 1

if executar and tema:
    st.session_state.passo = carregar_progresso(tema)

# ---------------------------
# Verificação de entrada
# ---------------------------
if not tema or not api_key:
    st.stop()

# ---------------------------
# Função robusta para chamar o modelo com retries
# ---------------------------
def criar_llm(model_name="groq/llama-3.3-70b-versatile"):
    """Cria um LLM configurado para o Groq."""
    return LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.3
    )

def executar_com_retry(funcao, tentativas=3, espera=5):
    """Executa uma função com tentativas em caso de RateLimitError."""
    for i in range(tentativas):
        try:
            return funcao()
        except RateLimitError as e:
            if i < tentativas - 1:
                st.warning(f"⏳ Limite atingido, aguardando {espera} segundos antes de tentar novamente...")
                time.sleep(espera)
            else:
                st.error("❌ Limite de requisições excedido repetidamente. Trocando para modelo alternativo.")
                return None
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            return None
    return None

# ---------------------------
# Criação inicial do LLM
# ---------------------------
llm = criar_llm()

# ---------------------------
# Agentes
# ---------------------------
agente_teoria = Agent(
    role="Instrutor(a) de GML",
    goal=(
        "Ensinar o conceito de {tema} em GML de forma clara e prática, adequada para {nivel}."
    ),
    backstory="Instrutor veterano de GameMaker Studio 2, focado em clareza e exemplos simples.",
    llm=llm, verbose=False
)

agente_exemplos = Agent(
    role="Criador(a) de Exemplos de Código GML",
    goal="Gerar exemplos curtos, comentados e úteis de código GML sobre {tema}.",
    backstory="Cria exemplos reais e diretos de uso do GML.",
    llm=llm, verbose=False
)

agente_projetos = Agent(
    role="Designer(a) de Mini-Projetos GML",
    goal="Desenvolver um mini-projeto prático e curto sobre {tema}, com código base e explicação.",
    backstory="Transforma teoria de GML em mini-projetos práticos para GameMaker Studio 2.",
    llm=llm, verbose=False
)

# ---------------------------
# Tarefas
# ---------------------------
t_teoria = Task(
    description="PASSO 1 - Explique o conceito de {tema} em GML de modo didático e aplicado.",
    agent=agente_teoria,
    expected_output="Explicação em Markdown."
)

t_exemplos = Task(
    description="PASSO 2 - Crie 3 exemplos curtos e comentados de código GML sobre {tema}.",
    agent=agente_exemplos,
    expected_output="Lista de exemplos com ```gml```."
)

t_projeto = Task(
    description="PASSO 3 - Desenvolva um mini-projeto prático sobre {tema}, com código base.",
    agent=agente_projetos,
    expected_output="Mini-projeto com código GML e explicações."
)

# ---------------------------
# Execução das tarefas com tratamento de rate limit
# ---------------------------
crew = Crew(
    agents=[agente_teoria, agente_exemplos, agente_projetos],
    tasks=[t_teoria, t_exemplos, t_projeto],
    process=Process.sequential,
)

def rodar_tarefas():
    try:
        crew.kickoff(inputs={
            "tema": tema,
            "nivel": nivel or "iniciante",
            "objetivo": objetivo or "aprender GML de forma prática"
        })
    except RateLimitError:
        st.warning("⚠️ Limite de tokens atingido — aguardando e tentando novamente...")
        time.sleep(5)
        try:
            crew.kickoff(inputs={
                "tema": tema,
                "nivel": nivel or "iniciante",
                "objetivo": objetivo or "aprender GML de forma prática"
            })
        except RateLimitError:
            st.error("❌ Ainda atingindo o limite. Trocando para modelo alternativo menor...")
            alt_llm = criar_llm("groq/llama-3.1-8b-instant")
            for agente in [agente_teoria, agente_exemplos, agente_projetos]:
                agente.llm = alt_llm
            crew.kickoff(inputs={
                "tema": tema,
                "nivel": nivel or "iniciante",
                "objetivo": objetivo or "aprender GML de forma prática"
            })

# Executa com segurança
executar_com_retry(rodar_tarefas, tentativas=3, espera=6)

# ---------------------------
# Resultados
# ---------------------------
teoria_out = getattr(t_teoria, "output", "") or getattr(t_teoria, "result", "")
exemplos_out = getattr(t_exemplos, "output", "") or getattr(t_exemplos, "result", "")
projeto_out = getattr(t_projeto, "output", "") or getattr(t_projeto, "result", "")

# ---------------------------
# Interface passo a passo
# ---------------------------
st.markdown("---")
st.subheader(f"🧭 Etapa {st.session_state.passo} de 3 — {tema.title()}")

if st.session_state.passo == 1:
    st.markdown("### 📘 Teoria")
    st.markdown(teoria_out)
elif st.session_state.passo == 2:
    st.markdown("### 💡 Exemplos")
    st.markdown(exemplos_out)
elif st.session_state.passo == 3:
    st.markdown("### 🎯 Mini-Projeto")
    st.markdown(projeto_out)
else:
    st.success(f"🎉 Parabéns! Você concluiu o tutorial de **{tema.title()}** em GML!")

# ---------------------------
# Navegação + salvamento
# ---------------------------
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.session_state.passo > 1:
        if st.button("⬅️ Voltar"):
            st.session_state.passo -= 1
            salvar_progresso(tema, st.session_state.passo)
            st.rerun()

with col2:
    st.markdown(f"<div style='text-align:center;font-weight:bold;'>Etapa {st.session_state.passo}/3</div>", unsafe_allow_html=True)

with col3:
    if st.session_state.passo < 3:
        if st.button("➡️ Próximo"):
            st.session_state.passo += 1
            salvar_progresso(tema, st.session_state.passo)
            st.rerun()
    else:
        if st.button("✅ Finalizar"):
            st.session_state.passo = 4
            salvar_progresso(tema, 1)
            st.success(f"Tutorial de **{tema.title()}** concluído! Progresso reiniciado para próxima revisão.")
            st.rerun()