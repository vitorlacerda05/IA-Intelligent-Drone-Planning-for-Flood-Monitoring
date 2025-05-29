import pandas as pd
import folium
import math
from collections import deque

# =====================
# 1. Lista de Capitais Brasileiras (nome, lat, lon)
# =====================
CAPITAIS = [
    {"nome": "Rio Branco", "lat": -9.97499, "lon": -67.8243},
    {"nome": "Maceió", "lat": -9.66599, "lon": -35.735},
    {"nome": "Macapá", "lat": 0.034934, "lon": -51.0694},
    {"nome": "Manaus", "lat": -3.10194, "lon": -60.025},
    {"nome": "Salvador", "lat": -12.9718, "lon": -38.5011},
    {"nome": "Fortaleza", "lat": -3.71722, "lon": -38.5431},
    {"nome": "Brasília", "lat": -15.7797, "lon": -47.9297},
    {"nome": "Vitória", "lat": -20.3155, "lon": -40.3128},
    {"nome": "Goiânia", "lat": -16.6864, "lon": -49.2643},
    {"nome": "São Luís", "lat": -2.53073, "lon": -44.3068},
    {"nome": "Cuiabá", "lat": -15.6014, "lon": -56.0974},
    {"nome": "Campo Grande", "lat": -20.4486, "lon": -54.6295},
    {"nome": "Belo Horizonte", "lat": -19.9208, "lon": -43.9378},
    {"nome": "Belém", "lat": -1.45502, "lon": -48.5024},
    {"nome": "João Pessoa", "lat": -7.11509, "lon": -34.8641},
    {"nome": "Curitiba", "lat": -25.4284, "lon": -49.2733},
    {"nome": "Recife", "lat": -8.04756, "lon": -34.877},
    {"nome": "Teresina", "lat": -5.08921, "lon": -42.8016},
    {"nome": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
    {"nome": "Natal", "lat": -5.79448, "lon": -35.211},
    {"nome": "Porto Alegre", "lat": -30.0346, "lon": -51.2177},
    {"nome": "Porto Velho", "lat": -8.76077, "lon": -63.8999},
    {"nome": "Boa Vista", "lat": 2.82384, "lon": -60.6753},
    {"nome": "Florianópolis", "lat": -27.5954, "lon": -48.548},
    {"nome": "São Paulo", "lat": -23.5505, "lon": -46.6333},
    {"nome": "Aracaju", "lat": -10.9472, "lon": -37.0731},
    {"nome": "Palmas", "lat": -10.2491, "lon": -48.3243},
]

# =====================
# 2. Parâmetros do Drone
# =====================
AUTONOMIA_MAX = 750.0  # km
MAX_ITERATIONS = 10000

# =====================
# 3. Função de Distância Haversine
# =====================
def haversine(coord1, coord2):
    R = 6371  # raio da Terra em km
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def distancia_entre_cidades(cidade1, cidade2):
    return haversine((cidade1["lat"], cidade1["lon"]), (cidade2["lat"], cidade2["lon"]))

# =====================
# 4. Leitura dos Dados de Alagamentos
# =====================
df = pd.read_excel("database/alagamentos-filtred.xlsx")
# Cada cidade: {"lat": float, "lon": float}
all_flood_cities = [
    {"lat": row["lat"], "lon": row["long"]} for _, row in df.iterrows()
]

# =====================
# 5. Funções Auxiliares
# =====================
def encontrar_capital_mais_proxima(coord, capitais):
    menor_dist = float("inf")
    capital_mais_proxima = None
    for capital in capitais:
        dist = haversine((coord["lat"], coord["lon"]), (capital["lat"], capital["lon"]))
        if dist < menor_dist:
            menor_dist = dist
            capital_mais_proxima = capital
    return capital_mais_proxima, menor_dist

def encontrar_cidade_mais_proxima(coord, cidades, visitadas):
    menor_dist = float("inf")
    cidade_mais_proxima = None
    idx_mais_proxima = None
    for idx, cidade in enumerate(cidades):
        if idx in visitadas:
            continue
        dist = haversine((coord["lat"], coord["lon"]), (cidade["lat"], cidade["lon"]))
        if dist < menor_dist:
            menor_dist = dist
            cidade_mais_proxima = cidade
            idx_mais_proxima = idx
    return idx_mais_proxima, cidade_mais_proxima, menor_dist

# =====================
# 6. Algoritmo de Planejamento (A* Guloso)
# =====================
def drone_planning():
    caminho = []  # lista de tuplas: (tipo, origem, destino, distancia)
    cidades_visitadas = set()
    reabastecimentos = 0
    iter_count = 0
    
    # Começa em SP
    capital_atual = next(c for c in CAPITAIS if c["nome"] == "São Paulo")
    pos_atual = {"lat": capital_atual["lat"], "lon": capital_atual["lon"]}
    autonomia_restante = AUTONOMIA_MAX
    
    while len(cidades_visitadas) < len(all_flood_cities) and iter_count < MAX_ITERATIONS:
        iter_count += 1
        idx, cidade, dist = encontrar_cidade_mais_proxima(pos_atual, all_flood_cities, cidades_visitadas)
        if cidade is None:
            break
        if dist <= autonomia_restante:
            caminho.append(("vermelha", pos_atual, cidade, dist))
            cidades_visitadas.add(idx)
            pos_atual = cidade
            autonomia_restante -= dist
        else:
            # Verifica se existe alguma cidade que pode ser visitada após reabastecer
            capital_proxima, dist_cap = encontrar_capital_mais_proxima(pos_atual, CAPITAIS)
            pode_visitar_apos_reabastecer = False
            for i, c in enumerate(all_flood_cities):
                if i in cidades_visitadas:
                    continue
                dist_da_capital = haversine((capital_proxima["lat"], capital_proxima["lon"]), (c["lat"], c["lon"]))
                if dist_da_capital <= AUTONOMIA_MAX:
                    pode_visitar_apos_reabastecer = True
                    break
            if not pode_visitar_apos_reabastecer:
                # Não há mais cidades possíveis após reabastecer, finalizar na capital
                caminho.append(("azul", pos_atual, capital_proxima, dist_cap))
                pos_atual = {"lat": capital_proxima["lat"], "lon": capital_proxima["lon"]}
                break
            caminho.append(("azul", pos_atual, capital_proxima, dist_cap))
            pos_atual = {"lat": capital_proxima["lat"], "lon": capital_proxima["lon"]}
            autonomia_restante = AUTONOMIA_MAX
            reabastecimentos += 1
    # Finaliza em uma capital se não terminou lá
    capital_final, dist_final = encontrar_capital_mais_proxima(pos_atual, CAPITAIS)
    if pos_atual["lat"] != capital_final["lat"] or pos_atual["lon"] != capital_final["lon"]:
        caminho.append(("azul", pos_atual, capital_final, dist_final))
    return caminho, len(cidades_visitadas), reabastecimentos

# =====================
# 7. Visualização com Folium
# =====================
def plotar_rota_folium(caminho, cidades_visitadas, reabastecimentos):
    m = folium.Map([-14.5931291, -56.6985808], zoom_start=4)
    
    # Identificar capital de início e capital de fim
    capital_inicio = CAPITAIS[24]  # São Paulo
    # Capital de fim: última capital visitada (último destino de linha amarela)
    capital_fim = None
    for tipo, origem, destino, dist in reversed(caminho):
        if tipo == "azul" or tipo == "orange":
            # Encontrar capital correspondente
            for cap in CAPITAIS:
                if abs(cap["lat"] - destino["lat"]) < 1e-5 and abs(cap["lon"] - destino["lon"]) < 1e-5:
                    capital_fim = cap
                    break
            if capital_fim:
                break
    
    # Marcar capitais
    for capital in CAPITAIS:
        # Início
        if abs(capital["lat"] - capital_inicio["lat"]) < 1e-5 and abs(capital["lon"] - capital_inicio["lon"]) < 1e-5:
            folium.Marker(
                [capital["lat"], capital["lon"]],
                popup=f"Capital de Início: {capital['nome']}<br>Lat: {capital['lat']:.4f}<br>Lon: {capital['lon']:.4f}",
                icon=folium.Icon(color="green", icon="play", prefix="fa")
            ).add_to(m)
        # Fim
        elif capital_fim and abs(capital["lat"] - capital_fim["lat"]) < 1e-5 and abs(capital["lon"] - capital_fim["lon"]) < 1e-5:
            folium.Marker(
                [capital["lat"], capital["lon"]],
                popup=f"Capital de Fim: {capital['nome']}<br>Lat: {capital['lat']:.4f}<br>Lon: {capital['lon']:.4f}",
                icon=folium.Icon(color="purple", icon="stop", prefix="fa")
            ).add_to(m)
        else:
            folium.Marker(
                [capital["lat"], capital["lon"]],
                popup=f"{capital['nome']}<br>Lat: {capital['lat']:.4f}<br>Lon: {capital['lon']:.4f}",
                icon=folium.Icon(color="blue", icon="flag")
            ).add_to(m)
    
    # Marcar cidades visitadas (vermelho)
    for idx in cidades_visitadas:
        cidade = all_flood_cities[idx]
        folium.CircleMarker(
            [cidade["lat"], cidade["lon"]],
            radius=4, color="red", fill=True, fill_color="red",
            popup=f"Cidade visitada<br>Lat: {cidade['lat']:.4f}<br>Lon: {cidade['lon']:.4f}"
        ).add_to(m)
    
    # Marcar cidades NÃO visitadas (amarelo claro)
    for idx, cidade in enumerate(all_flood_cities):
        if idx not in cidades_visitadas:
            folium.CircleMarker(
                [cidade["lat"], cidade["lon"]],
                radius=4, color="#ffe066", fill=True, fill_color="#ffe066",
                popup=f"Cidade NÃO visitada<br>Lat: {cidade['lat']:.4f}<br>Lon: {cidade['lon']:.4f}"
            ).add_to(m)
    
    # Desenhar rotas
    distancia_total = 0
    for tipo, origem, destino, dist in caminho:
        cor = "red" if tipo == "vermelha" else "orange"
        distancia_total += dist
        folium.PolyLine(
            [[origem["lat"], origem["lon"]], [destino["lat"], destino["lon"]]],
            color=cor, weight=4, opacity=0.7,
            tooltip=f"{dist:.1f} km"
        ).add_to(m)
    
    # Legenda customizada
    legenda_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: auto; height: auto; 
                 background-color: white; z-index:9999; font-size:14px;
                 border:2px solid grey; border-radius:8px; padding: 10px;">
     <b>Legenda:</b>
     <br>
     <br>
     <svg width="20" height="8"><line x1="0" y1="4" x2="20" y2="4" style="stroke:red;stroke-width:4"/></svg> Trecho entre cidades visitadas<br>
     <svg width="20" height="8"><line x1="0" y1="4" x2="20" y2="4" style="stroke:orange;stroke-width:4"/></svg> Reabastecimento<br>
     <i class="fa fa-play fa-1x" style="color:green"></i> Capital de início<br>
     <i class="fa fa-stop fa-1x" style="color:purple"></i> Capital de fim<br>
     <i class="fa fa-flag fa-1x" style="color:blue"></i> Capital<br>
     <svg width="16" height="16"><circle cx="8" cy="8" r="6" fill="red"/></svg> Cidade visitada<br>
     <svg width="16" height="16"><circle cx="8" cy="8" r="6" fill="#ffe066" stroke="#ffe066"/></svg> Cidade não visitada<br>
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legenda_html))

    # Caixa de informações no canto superior direito
    tempo_total = distancia_total / 100.0  # 100 km/h
    info_html = f'''
    <div style="position: fixed; top: 50px; right: 50px; width: auto; height: auto; 
                background-color: white; z-index:9999; font-size:15px;
                border:2px solid #444; border-radius:8px; padding: 12px; box-shadow: 2px 2px 8px #888;">
        <b>Resumo da Missão</b>
        <br>
        <br>
        Distância total: <b>{distancia_total:.1f} km</b><br>
        Tempo total: <b>{tempo_total:.1f} h</b><br>
        Cidades visitadas: <b>{len(cidades_visitadas)}</b><br>
        Reabastecimentos: <b>{reabastecimentos}</b>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(info_html))

    m.save("rota_drone.html")
    print(f"Cidades visitadas: {len(cidades_visitadas)} | Reabastecimentos: {reabastecimentos}")
    print("Mapa salvo como rota_drone.html")

# =====================
# 8. Execução Principal
# =====================
def encontrar_melhor_capital_inicial(all_flood_cities):
    melhor_capital = None
    melhor_score = -1
    melhor_cidades = -1
    melhor_resultado = None
    for capital in CAPITAIS:
        caminho, cidades_visitadas, n_reabastecimentos = drone_planning_custom_inicio(all_flood_cities, capital['nome'])
        cidades = len(cidades_visitadas)
        reab = n_reabastecimentos if n_reabastecimentos > 0 else 1
        score = cidades / reab
        # Prioriza maior score, depois maior número absoluto de cidades
        if score > melhor_score or (score == melhor_score and cidades > melhor_cidades):
            melhor_score = score
            melhor_capital = capital['nome']
            melhor_cidades = cidades
            melhor_resultado = (caminho, cidades_visitadas, n_reabastecimentos)
    return melhor_capital, melhor_resultado

def drone_planning_custom_inicio(all_flood_cities, capital_nome):
    caminho = []
    cidades_visitadas = set()
    reabastecimentos = 0
    iter_count = 0
    capital_atual = next(c for c in CAPITAIS if c["nome"] == capital_nome)
    pos_atual = {"lat": capital_atual["lat"], "lon": capital_atual["lon"]}
    autonomia_restante = AUTONOMIA_MAX
    while len(cidades_visitadas) < len(all_flood_cities) and iter_count < MAX_ITERATIONS:
        iter_count += 1
        idx, cidade, dist = encontrar_cidade_mais_proxima(pos_atual, all_flood_cities, cidades_visitadas)
        if cidade is None:
            break
        if dist <= autonomia_restante:
            caminho.append(("vermelha", pos_atual, cidade, dist))
            cidades_visitadas.add(idx)
            pos_atual = cidade
            autonomia_restante -= dist
        else:
            capital_proxima, dist_cap = encontrar_capital_mais_proxima(pos_atual, CAPITAIS)
            pode_visitar_apos_reabastecer = False
            for i, c in enumerate(all_flood_cities):
                if i in cidades_visitadas:
                    continue
                dist_da_capital = haversine((capital_proxima["lat"], capital_proxima["lon"]), (c["lat"], c["lon"]))
                if dist_da_capital <= AUTONOMIA_MAX:
                    pode_visitar_apos_reabastecer = True
                    break
            if not pode_visitar_apos_reabastecer:
                caminho.append(("azul", pos_atual, capital_proxima, dist_cap))
                pos_atual = {"lat": capital_proxima["lat"], "lon": capital_proxima["lon"]}
                break
            caminho.append(("azul", pos_atual, capital_proxima, dist_cap))
            pos_atual = {"lat": capital_proxima["lat"], "lon": capital_proxima["lon"]}
            autonomia_restante = AUTONOMIA_MAX
            reabastecimentos += 1
    capital_final, dist_final = encontrar_capital_mais_proxima(pos_atual, CAPITAIS)
    if pos_atual["lat"] != capital_final["lat"] or pos_atual["lon"] != capital_final["lon"]:
        caminho.append(("azul", pos_atual, capital_final, dist_final))
    return caminho, cidades_visitadas, reabastecimentos

def main():
    df = pd.read_excel("database/alagamentos-filtred.xlsx")
    all_flood_cities = [
        {"lat": row["lat"], "lon": row["long"]} for _, row in df.iterrows()
    ]
    melhor_capital, melhor_resultado = encontrar_melhor_capital_inicial(all_flood_cities)
    print(f"Melhor capital inicial: {melhor_capital}")
    caminho, cidades_visitadas, n_reabastecimentos = melhor_resultado
    plotar_rota_folium(caminho, cidades_visitadas, n_reabastecimentos)

if __name__ == "__main__":
    main() 