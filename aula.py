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

tema = st.text_input("Terra de estudo", placeholder="Ex.:Algoritimos") #enquanto nao tiver texto, o comando placeholder vai deixar essa mensagem
objetivo = st.text_input("Objetivo", placeholder="Ex.: Entender Conceitos")

executar= st.button("Gerar material")
api_key = "" #se pega no groq 

if executar:
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
    agente_gabarito = Agent(
        role = "Revisor e gabaritor.",
        goal =(
            "Ler os EXERCÍCIOS sobre {tema} e produzir o GABARITO oficial,"
            "com respostas corretas e justificativa breve (1-3) por item"
            "Variar formato (múltipla escolha, V/F, completar, resolução curta)."
            "Enunciados claros. NÃO incluir respostas"
        ),
        backstory = "Você confere consistência e explica rapidamente o porquê das resposta",
        llm=llm, verbose = False
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
    t_gabarito = Task(
        description=(
            "GABARITO: Com base nos EXERCÍCIOS fornecidos no contexto, produza as respostas corretas."
            "Para cada item, de: \n"
            "- Resposta: (letra, valor, solução)\n"
            "-Comentários: justificativa breve e direta (1-2), citando o conceito-chave"
            "Formato: lista numerada (1 a 3) em Markdown."
        ),
        agent=agente_gabarito,
        expected_output="Lista numerada (1-3) em Markdown com resposta e comentário por exercício"
        context=[t_exercicios]
    )

    #definindo equipe
    agents = [agente_resumo, agente_exemplos, agente_exercicios, agente_gabarito]
    tasks = [t_resumo, t_exemplos, t_exercicios, t_gabarito]
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential
    )

    crew.kickoff(input={
        "tema": tema,
        "objetivo": objetivo or "não informado"
    })

    resumo_out = getattr(t_resumo, "output", None) or getattr(t_resumo, "result", "") or ""
    exemplo_out = getattr(t_exemplos, "output", None) or getattr(t_exemplos, "result", "") or ""
    exercicio_out = getattr(t_exercicios, "output", None) or getattr(t_exercicios, "result", "") or ""
    gabarito_out = getattr(t_gabarito, "output", None) or getattr(t_gabarito, "result", "") or ""