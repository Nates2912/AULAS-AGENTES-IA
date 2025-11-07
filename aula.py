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