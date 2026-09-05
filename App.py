import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURAÇÃO DA TELA
st.set_page_config(page_title="Nosso Simulador Bet", layout="wide")
st.title("⚽ Nosso Simulador de Apostas Privado")

# CONFIGURAÇÃO DE SEGURANÇA - SUA CHAVE JÁ INCLUÍDA
API_KEY = "9031cb9c4acdf3a6f3f6834b8600a2af"
SPORT = "soccer_epl" 
REGIONS = "eu"

# 2. SISTEMA DE SALDO VIRTUAL (Guarda as informações enquanto o app está aberto)
if "saldo" not in st.session_state:
    st.session_state.saldo = 1000.0  # Todo mundo começa com 1000 créditos fictícios
if "historico_apostas" not in st.session_state:
    st.session_state.historico_apostas = []

# Exibe o saldo no topo da tela de forma elegante
st.metric(label="💰 Seu Saldo Virtual", value=f"R$ {st.session_state.saldo:,.2f}")

st.write("---")
st.subheader("📋 Próximos Jogos & Painel de Apostas")

# 3. BUSCA DE DADOS EM TEMPO REAL
url = f"https://the-odds-api.com{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets=h2h"

try:
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        
        if not dados:
            st.info("Nenhum jogo encontrado para esta liga no momento.")
        else:
            # Criando o painel jogo por jogo
            for idx, jogo in enumerate(dados[:5]): # Mostra os 5 primeiros jogos para ficar organizado
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

                # Criando um bloco visual para cada jogo
                with st.container():
                    col1, col2, col3 = st.columns([2, 3, 2])
                    
                    with col1:
                        st.write(f"**{home_team}** vs **{away_team}**")
                    
                    with col2:
                        # Botões de escolha do palpite
                        escolha = st.radio(
                            f"Escolha seu palpite para o Jogo {idx+1}: ",
                            [f"Casa ({odd_casa})", f"Empate ({odd_empate})", f"Fora ({odd_fora})"],
                            horizontal=True,
                            key=f"radio_{idx}"
                        )
                    
                    with col3:
                        # Campo para digitar o valor da aposta fictícia
                        valor_aposta = st.number_input("Valor do Palpite (R$):", min_value=0.0, max_value=st.session_state.saldo, step=10.0, key=f"num_{idx}")
                        
                        if st.button("Confirmar Palpite Fictício", key=f"btn_{idx}"):
                            if valor_aposta > 0:
                                st.session_state.saldo -= valor_aposta
                                
                                # Extrai apenas o número da odd do texto do botão de rádio
                                odd_selecionada = odd_casa if "Casa" in escolha else (odd_empate if "Empate" in escolha else odd_fora)
                                possivel_retorno = valor_aposta * odd_selecionada
                                
                                # Salva no histórico do app
                                st.session_state.historico_apostas.append({
                                    "Jogo": f"{home_team} vs {away_team}",
                                    "Seu Palpite": escolha.split(" ")[0],
                                    "Valor Guardado": f"R$ {valor_aposta:.2f}",
                                    "Retorno Potencial": f"R$ {possivel_retorno:.2f}"
                                })
                                st.success("Palpite registrado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Insira um valor maior que R$ 0")
                st.write("---")
    else:
        st.error(f"Erro ao conectar com o mercado de Odds. Verifique o limite da chave.")
except Exception as e:
    st.error(f"Erro no sistema: {e}")

# 4. HISTÓRICO DE PALPITES DO GRUPO
if st.session_state.historico_apostas:
    st.subheader("🗒️ Seus Palpites Registrados (Simulação)")
    df_historico = pd.DataFrame(st.session_state.historico_apostas)
    st.dataframe(df_historico, use_container_width=True)
