#AGENTE = ESPECIALIZADO/FUNÇÃO
#TAREFA 1 = AGENTE 1
#AGENTE 2 = AGENTE(RESULTADO 1)

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM #LLM é a sigla para "Large Language Model" (Grande Modelo de Linguagem)  
                                                   #um tipo de inteligência artificial treinado em grandes volumes de dados de texto
                                                   #para compreender
                                                   #gerar e manipular texto de forma humana
                                                   #quantos mais parametros, mais "raciocinio" a IA tem

#Agentes para estudo

st.header("📖Agentes para estudo📖")
st.write("Informe o tema e gere material para estudar: ")

tema = st.text_input("Tema de estudo", placeholder="Ex.:Algoritimos") #enquanto nao tiver texto, o comando placeholder vai deixar essa mensagem
nivel = st.text_input("Público/nível (opcional)", placeholder="Ex.: iniciante, ensino médio, graduação, profissional")
objetivo = st.text_area("Objetivo (opcional)", placeholder="Ex.: entender conceitos básicos e aplicar em exercícios simples")


# NOVO: toggle para gabarito
mostrar_gabarito = st.toggle("Gerar e mostrar gabarito (respostas + justificativas)", value=True)


executar= st.button("Gerar material")
api_key = "" #se pega no groq 



if executar:
    if not api_key or not tema:
        st.error("Por favor, informe a API key e o tema de estudo.")
        st.stop()

    llm = LLM(
        model = "groq/llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.3 #temperature define o nivel de criatividade.
        # <= 0.3 mais deterministico,
        # entre 0.4 e 0.7 equilibrado para explicação,
        # maior que 0.7 mais criativo e menos previsivel
    )
    agente_resumo = Agent(
        role = "Redator de resumo didático.",
        goal =(
            "Escrever RESUMO claro e didático {tema} alinhado com o {objetivo}."
            "A linguagem deve ser didática, direta com contexto prático e sem jargões."
        ),
        backstory = "Você transforma temas técnicos/acadêmicos em explicações curtas e precisas",
        llm=llm, verbose = False
    )
    agente_exemplos = Agent(
        role = "Criador de exemplos contextualizados.",
        goal =(
            "Gerar 5 EXEMPLOS CURTOS sobre {tema}, cada um com contexto realista ."
            "Cada exemplo com título (em negrito), cenário, dados (se houver) aplicação e resultados."
        ),
        backstory = "Você mostra o conceito em acçao com exemplos breves e concretos",
        llm=llm, verbose = False
    )
    agente_exercicios = Agent(
        role = "Criador de exemplos práticos.",
        goal =(
            "Criar 4 EXERCÍCIOS SIMPLES sobre {tema}."
            "Variar formato (múltipla escolha, V/F, completar, resolução curta)."
            "Enunciados claros. NÃO incluir respostas"
        ),
        backstory = "Você cria atividades rápidas que fixam os conceitos essenciais",
        llm=llm, verbose = False
    )

    # Opcional: agente de gabarito (só se toggle estiver ligado)
    if mostrar_gabarito:
        agente_gabarito = Agent(
            role="Revisor(a) e Gabaritador(a)",
            goal=(
                "Ler os EXERCÍCIOS sobre {tema} e produzir o GABARITO oficial, "
                "com respostas corretas e justificativa breve (1–2 frases) por item."
            ),
            backstory="Você confere consistência e explica rapidamente o porquê da resposta.",
            llm=llm, verbose=False
    )

    t_resumo = Task(
        description=(
            "RESUMO: escreva em português do Brasil um resumo didático sobre {tema} e objetivo {objetivo}"
            "Inclua: definição (3-4 frases), por que importa (2-3), onde se aplica (2,3) e 4,6 ideias chave,"
            "com marcadores. Formate em Markdown com título, parágrafos curtos e com 4-6 marcadores"
        ),
        agent=agente_resumo,
        expected_output="Resumo em Markdown com título, parágrafos curtos e 4-6 marcadores (bullets)."
    )
    t_exemplos = Task(
        description=(
            "EXEMPLOS: produza 4 exemplos curtos e contextualizados sobre {tema}"
            "Padrão (até 5 linhas cada): Título, cenário, dados/ entrada, como aplicar (1-2)frases, resultados"
            
        ),
        agent=agente_exemplos,
        expected_output="Lista numerada (1-4) em Markdown com exemplos curtos e completos"
    )
    t_exercicios = Task(
        description=(
            "EXERCÍCIOS: Crie 4 exercícios simples sobre o {tema} em PT-BR."
            "Varie formatos e não inclua respostas."
            "Entregue lista numerada (1-4) em Markdown"
            
        ),
        agent=agente_exercicios,
        expected_output="Lista numerada (1-4) em Markdown com exercícios simples, sem respostas"
    )

    if mostrar_gabarito:
        t_gabarito = Task(
            description=(
                "GABARITO\n"
                "Com base nos EXERCÍCIOS fornecidos no contexto, produza as respostas corretas dos itens 1–3. "
                "Para cada item, dê:\n"
                "- **Resposta:** (letra/valor/solução) \n"
                "- **Comentário:** justificativa breve e direta (1–2 frases), citando o conceito-chave.\n"
                "Formato: lista numerada (1 a 3) em Markdown."
            ),
            agent=agente_gabarito,
            expected_output="Lista numerada (1–3) com resposta e comentário por exercício.",
            context=[t_exercicios]
        )

    #definindo equipe
    agents = [agente_resumo, agente_exemplos, agente_exercicios]
    tasks = [t_resumo, t_exemplos, t_exercicios]
    if mostrar_gabarito:
        agents.append(agente_gabarito)
        tasks.append(t_gabarito)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
    )

    crew.kickoff(inputs={
        "tema": tema,
        "nivel": nivel or "não informado",
        "objetivo": objetivo or "não informado",
    })

    # ---------------------------
    # Exibição
    # ---------------------------
    resumo_out = getattr(t_resumo, "output", None) or getattr(t_resumo, "result", "") or ""
    exemplos_out = getattr(t_exemplos, "output", None) or getattr(t_exemplos, "result", "") or ""
    exercicios_out = getattr(t_exercicios, "output", None) or getattr(t_exercicios, "result", "") or ""
    gabarito_out = ""
    if mostrar_gabarito:
        gabarito_out = getattr(t_gabarito, "output", None) or getattr(t_gabarito, "result", "") or ""

    # Abas condicionais
    if mostrar_gabarito:
        aba_resumo, aba_exemplos, aba_exercicios, aba_gabarito = st.tabs(
            ["Resumo", "Exemplos", "Exercícios", "Gabarito"]
        )
    else:
        aba_resumo, aba_exemplos, aba_exercicios = st.tabs(
            ["Resumo", "Exemplos", "Exercícios"]
        )

    with aba_resumo:
        st.markdown(resumo_out)
    with aba_exemplos:
        st.markdown(exemplos_out)
    with aba_exercicios:
        st.markdown(exercicios_out)
    if mostrar_gabarito:
        with aba_gabarito:
            st.markdown(gabarito_out)