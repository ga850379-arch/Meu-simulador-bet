import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURAÇÃO DA TELA
st.set_page_config(page_title="Nosso Simulador Bet", layout="wide")
st.title("⚽ Nosso Simulador de Apostas Privado")

# CONFIGURAÇÃO DE SEGURANÇA - SUA CHAVE JÁ INCLUÍDA
API_KEY = "9031cb9c4acdf3a6f3f6834b8600a2af"
REGIONS = "us"  # Região alterada para garantir o carregamento na nuvem

# SISTEMA DE SALDO VIRTUAL
if "saldo" not in st.session_state:
    st.session_state.saldo = 1000.0
if "historico_apostas" not in st.session_state:
    st.session_state.historico_apostas = []

st.metric(label="💰 Seu Saldo Virtual", value=f"R$ {st.session_state.saldo:,.2f}")
st.write("---")
st.subheader("📋 Próximos Jogos & Painel de Apostas")

# Lista de ligas para tentar buscar (se a primeira falhar, tenta a próxima)
LIGAS_PARA_TESTAR = ["soccer_epl", "soccer_usa_mls", "soccer_uefa_champs_league"]
dados = None

# Tenta buscar jogos nas ligas disponíveis
for liga in LIGAS_PARA_TESTAR:
    url = f"https://the-odds-api.com{liga}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets=h2h"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_dados = response.json()
            if temp_dados:  # Se encontrou jogos nesta liga, usa ela
                dados = temp_dados
                break
    except Exception:
        pass

if not dados:
    st.error("⚠️ Não encontramos jogos ativos no momento ou o servidor bloqueou o acesso. Tente atualizar a página em alguns instantes.")
else:
    # Criando o painel jogo por jogo
    for idx, jogo in enumerate(dados[:5]):
        home_team = jogo["home_team"]
        away_team = jogo["away_team"]
        
        odd_casa, odd_fora, odd_empate = 1.0, 1.0, 1.0
        
        try:
            if jogo.get("bookmakers"):
                primeira_casa = jogo["bookmakers"][0]
                resultados = primeira_casa["markets"][0]["outcomes"]
                for resultado in resultados:
                    if resultado["name"] == home_team:
                        odd_casa = float(resultado["price"])
                    elif resultado["name"] == away_team:
                        odd_fora = float(resultado["price"])
                    elif resultado["name"].lower() in ["draw", "empate"]:
                        odd_empate = float(resultado["price"])
        except Exception:
            pass

        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                st.write(f"**{home_team}** vs **{away_team}**")
            
            with col2:
                escolha = st.radio(
                    f"Palpite para Jogo {idx+1}:",
                    [f"Casa ({odd_casa})", f"Empate ({odd_empate})", f"Fora ({odd_fora})"],
                    horizontal=True,
                    key=f"radio_{idx}"
                )
            
            with col3:
                valor_aposta = st.number_input("Valor (R$):", min_value=0.0, max_value=st.session_state.saldo, step=10.0, key=f"num_{idx}")
                
                if st.button("Confirmar Palpite", key=f"btn_{idx}"):
                    if valor_aposta > 0:
                        st.session_state.saldo -= valor_aposta
                        odd_selecionada = odd_casa if "Casa" in escolha else (odd_empate if "Empate" in escolha else odd_fora)
                        possivel_retorno = valor_aposta * odd_selecionada
                        
                        st.session_state.historico_apostas.append({
                            "Jogo": f"{home_team} vs {away_team}",
                            "Seu Palpite": escolha,
                            "Valor": f"R$ {valor_aposta:.2f}",
                            "Retorno Potencial": f"R$ {possivel_retorno:.2f}"
                        })
                        st.success("Palpite registrado!")
                        st.rerun()

        st.write("---")

# HISTÓRICO DE PALPITES
if st.session_state.historico_apostas:
    st.subheader("🗒️ Seus Palpites Registrados")
    df_historico = pd.DataFrame(st.session_state.historico_apostas)
    st.dataframe(df_historico, use_container_width=True)
