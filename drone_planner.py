import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2, ceil
from heapq import heappush, heappop
from typing import List, Set, Tuple, Dict, FrozenSet
import folium
from datetime import timedelta

class DronePlanner:
    def __init__(self, data_file: str, max_range: float = 750.0, speed: float = 100.0):
        """
        Initialize the drone planner with data and constraints.
        
        Args:
            data_file: Path to the Excel file containing flood data
            max_range: Maximum range of the drone in kilometers
            speed: Drone speed in km/h
        """
        self.max_range = max_range
        self.speed = speed  # km/h
        self.df = pd.read_excel(data_file)
        self.df = self.df.sample(50) 
        
        # Extract coordinates from localidade column
        self.df['lat'] = self.df['localidade'].apply(lambda x: float(x.split(',')[0]))
        self.df['lng'] = self.df['localidade'].apply(lambda x: float(x.split(',')[1]))
        
        # List of Brazilian capitals (simplified for example)
        self.capitals = {
            'Brasília': (-15.7801, -47.9292),
            'São Paulo': (-23.5505, -46.6333),
            'Rio de Janeiro': (-22.9068, -43.1729),
            'Belo Horizonte': (-19.9167, -43.9345),
            'Salvador': (-12.9714, -38.5014),
            'Recife': (-8.0476, -34.8770),
            'Fortaleza': (-3.7319, -38.5267),
            'Manaus': (-3.1190, -60.0217),
            'Curitiba': (-25.4284, -49.2733),
            'Porto Alegre': (-30.0346, -51.2177)
        }
        
        # Create a dictionary of all flooded cities with their coordinates
        self.flooded_cities = {
            row['localidade']: (row['lat'], row['lng'])
            for _, row in self.df.iterrows()
        }

        # Estimate average cities per leg (can be adjusted based on data analysis)
        self.estimated_cities_per_leg = 3

    def calculate_flight_time(self, distance: float) -> timedelta:
        """
        Calculate flight time based on distance and speed.
        
        Args:
            distance: Distance in kilometers
            
        Returns:
            Flight time as timedelta
        """
        hours = distance / self.speed
        return timedelta(hours=hours)

    def haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate the great circle distance between two points on the earth.
        
        Args:
            coord1: Tuple of (latitude, longitude) for first point
            coord2: Tuple of (latitude, longitude) for second point
            
        Returns:
            Distance in kilometers
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance

    def get_possible_legs(self, current_capital: str, visited_cities: FrozenSet[str]) -> List[Tuple[str, Set[str], float, timedelta]]:
        """
        Generate possible legs from current capital to other capitals, visiting unvisited flooded cities.
        
        Args:
            current_capital: Name of the current capital
            visited_cities: Set of already visited cities
            
        Returns:
            List of tuples (next_capital, cities_to_visit, total_distance, flight_time)
        """
        possible_legs = []
        current_coord = self.capitals[current_capital]
        
        # Try each possible destination capital
        for next_capital, next_coord in self.capitals.items():
            if next_capital == current_capital:
                continue
                
            # Get unvisited flooded cities
            unvisited = set(self.flooded_cities.keys()) - visited_cities
            
            # Try to find cities that can be visited along the way
            cities_to_visit = set()
            total_distance = 0
            
            # Sort cities by distance from current capital
            sorted_cities = sorted(
                unvisited,
                key=lambda city: self.haversine_distance(current_coord, self.flooded_cities[city])
            )
            
            # Try to add cities that don't exceed max range
            for city in sorted_cities:
                city_coord = self.flooded_cities[city]
                
                # Calculate new total distance if we add this city
                new_distance = (
                    self.haversine_distance(current_coord, city_coord) +
                    self.haversine_distance(city_coord, next_coord)
                )
                
                if new_distance <= self.max_range:
                    cities_to_visit.add(city)
                    total_distance = new_distance
                else:
                    break
            
            if cities_to_visit:
                flight_time = self.calculate_flight_time(total_distance)
                possible_legs.append((next_capital, cities_to_visit, total_distance, flight_time))
        
        return possible_legs

    def heuristic_astar(self, visited: frozenset) -> int:
        """
        Heurística para o A*: estima o número de paradas de reabastecimento restantes
        baseada no número de cidades não visitadas dividido pela média de cidades por trecho.
        """
        cidades_restantes = len(self.flooded_cities) - len(visited)
        return int(np.ceil(cidades_restantes / self.estimated_cities_per_leg))

    def find_optimal_route(self, start_capital: str) -> tuple:
        """
        Algoritmo A* para planejar a rota do drone:
        - Maximiza o número de cidades visitadas
        - Minimiza o número de paradas para reabastecimento
        - Usa f(n) = g(n) + h(n), onde:
            g(n): número de paradas de reabastecimento já realizadas
            h(n): estimativa de paradas restantes (heurística)
        """
        from heapq import heappush, heappop
        max_range = self.max_range
        flooded_cities = self.flooded_cities
        capitals = self.capitals
        all_cities = set(flooded_cities.keys())
        start_coord = capitals[start_capital]
        
        # Estado: (posição_atual, cidades_visitadas, autonomia_restante, capital_atual, caminho, paradas)
        initial_state = (start_coord, frozenset(), max_range, start_capital, [], 0)
        
        # Fila de prioridade: (f(n), -cidades_visitadas, paradas, estado)
        open_list = []
        g_score = {}
        state_id = (start_coord, frozenset(), max_range, start_capital)
        g_score[state_id] = 0
        f_score = g_score[state_id] + self.heuristic_astar(frozenset())
        heappush(open_list, (f_score, 0, 0, initial_state))
        
        best_visited = set()
        best_path = []
        best_paradas = float('inf')
        visited_states = dict()
        
        while open_list:
            f, neg_cities, paradas, state = heappop(open_list)
            pos, visited, autonomia, capital_atual, caminho, paradas = state
            
            # Atualiza melhor solução
            if len(visited) > len(best_visited) or (len(visited) == len(best_visited) and paradas < best_paradas):
                best_visited = visited
                best_path = caminho
                best_paradas = paradas
            
            # Se já visitou todas as cidades, pode parar
            if len(visited) == len(all_cities):
                break
            
            # 1. Tentar visitar cidades não visitadas dentro da autonomia
            for city, city_coord in flooded_cities.items():
                if city in visited:
                    continue
                dist = self.haversine_distance(pos, city_coord)
                if dist <= autonomia:
                    novo_visited = visited | {city}
                    novo_autonomia = autonomia - dist
                    novo_caminho = caminho + [("cidade", city, city_coord, novo_autonomia)]
                    novo_state = (city_coord, novo_visited, novo_autonomia, capital_atual, novo_caminho, paradas)
                    state_id = (city_coord, novo_visited, round(novo_autonomia, 2), capital_atual)
                    g = paradas
                    h = self.heuristic_astar(novo_visited)
                    f = g + h
                    if state_id not in visited_states or len(novo_visited) > len(visited_states[state_id]):
                        visited_states[state_id] = novo_visited
                        heappush(open_list, (f, -len(novo_visited), paradas, novo_state))
            # 2. Se autonomia não permite mais cidades, tentar reabastecer em qualquer capital (exceto onde já está)
            for cap, cap_coord in capitals.items():
                if cap == capital_atual:
                    continue
                dist = self.haversine_distance(pos, cap_coord)
                if dist <= autonomia:
                    novo_autonomia = max_range
                    novo_caminho = caminho + [("reabastecimento", cap, cap_coord, max_range)]
                    novo_state = (cap_coord, visited, max_range, cap, novo_caminho, paradas + 1)
                    state_id = (cap_coord, visited, max_range, cap)
                    g = paradas + 1
                    h = self.heuristic_astar(visited)
                    f = g + h
                    if state_id not in visited_states or len(visited) > len(visited_states[state_id]):
                        visited_states[state_id] = visited
                        heappush(open_list, (f, -len(visited), paradas + 1, novo_state))
        return best_path, len(best_visited)

    def _nearest_neighbor_order(self, start_coord, cities_coords):
        """
        Ordena as cidades pelo caminho mais próximo (nearest neighbor) a partir de start_coord.
        """
        if not cities_coords:
            return []
        ordered = []
        current = start_coord
        remaining = cities_coords.copy()
        while remaining:
            next_city = min(remaining, key=lambda c: self.haversine_distance(current, c))
            ordered.append(next_city)
            remaining.remove(next_city)
            current = next_city
        return ordered

    def visualize_route(self, path: list, output_file: str = 'drone_route.html'):
        """
        Visualiza o caminho retornado pelo novo A*.
        Args:
            path: lista de tuplas ("cidade" ou "reabastecimento", nome, coord, autonomia_restante)
            output_file: arquivo HTML de saída
        """
        import folium
        m = folium.Map([-14.5931291, -56.6985808], zoom_start=4)
        # Marcar capitais
        for capital, coord in self.capitals.items():
            folium.Marker(
                coord,
                popup=f"Capital: {capital}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        # Marcar cidades visitadas
        for step in path:
            tipo, nome, coord, autonomia = step
            if tipo == "cidade":
                folium.Marker(
                    coord,
                    popup=f"Cidade: {nome}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)
        # Desenhar rotas
        for i in range(1, len(path)):
            tipo_ant, nome_ant, coord_ant, _ = path[i-1]
            tipo, nome, coord, _ = path[i]
            if tipo == "cidade" and tipo_ant == "cidade":
                # Linha vermelha entre cidades
                folium.PolyLine(
                    [coord_ant, coord],
                    color='red',
                    weight=2,
                    opacity=0.8,
                    popup=f"De {nome_ant} para {nome}"
                ).add_to(m)
            elif tipo == "reabastecimento":
                # Linha amarela do último ponto até a capital
                folium.PolyLine(
                    [coord_ant, coord],
                    color='yellow',
                    weight=3,
                    opacity=0.8,
                    popup=f"Reabastecimento em {nome}"
                ).add_to(m)
        m.save(output_file)

    def greedy_route(self, start_capital: str):
        """
        Estratégia gulosa: sempre visita a cidade mais próxima dentro da autonomia restante.
        Quando não for possível, vai para a capital mais próxima para reabastecer.
        """
        current_pos = self.capitals[start_capital]
        current_capital = start_capital
        autonomy = self.max_range
        visited = set()
        path = []
        flooded_cities = self.flooded_cities.copy()
        capitals = self.capitals

        while len(visited) < len(flooded_cities):
            # Cidades não visitadas e dentro da autonomia
            candidates = [
                (city, coord, self.haversine_distance(current_pos, coord))
                for city, coord in flooded_cities.items()
                if city not in visited and self.haversine_distance(current_pos, coord) <= autonomy
            ]
            if candidates:
                # Escolhe a cidade mais próxima
                city, coord, dist = min(candidates, key=lambda x: x[2])
                path.append(("cidade", city, coord, autonomy - dist))
                autonomy -= dist
                current_pos = coord
                visited.add(city)
            else:
                # Não há cidades acessíveis, vai para a capital mais próxima para reabastecer
                capitals_candidates = [
                    (cap, coord, self.haversine_distance(current_pos, coord))
                    for cap, coord in capitals.items()
                    if cap != current_capital and self.haversine_distance(current_pos, coord) <= autonomy
                ]
                if not capitals_candidates:
                    break  # Não há como reabastecer, termina
                cap, coord, dist = min(capitals_candidates, key=lambda x: x[2])
                path.append(("reabastecimento", cap, coord, self.max_range))
                autonomy = self.max_range
                current_pos = coord
                current_capital = cap
        return path, len(visited) 