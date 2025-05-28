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

    def heuristic(self, visited_cities: FrozenSet[str]) -> float:
        """
        Heuristic function estimating remaining legs needed.
        
        Args:
            visited_cities: Set of visited cities
            
        Returns:
            Estimated number of remaining legs
        """
        remaining_cities = len(self.flooded_cities) - len(visited_cities)
        return ceil(remaining_cities / self.estimated_cities_per_leg)

    def find_optimal_route(self, start_capital: str) -> Tuple[List[Tuple[str, Set[str], float, timedelta]], int]:
        """
        Find optimal route using A* algorithm.
        
        Args:
            start_capital: Starting capital city
            
        Returns:
            Tuple of (route, total_cities_visited)
        """
        # Priority queue for A* search
        open_list = []
        # Set of visited states
        closed_set = set()
        # Dictionary to store best path to each state
        came_from = {}
        # Dictionary to store g scores
        g_score = {}
        
        # Initial state
        initial_state = (start_capital, frozenset())
        g_score[initial_state] = 0
        f_score = self.heuristic(frozenset())
        
        # Add initial state to open list
        heappush(open_list, (f_score, id(initial_state), initial_state))
        
        best_state = initial_state
        best_cities_visited = 0
        
        while open_list:
            # Get state with lowest f score
            _, _, current_state = heappop(open_list)
            current_capital, visited_cities = current_state
            
            # Skip if already visited
            if current_state in closed_set:
                continue
                
            # Update best state if this one visits more cities
            if len(visited_cities) > best_cities_visited:
                best_state = current_state
                best_cities_visited = len(visited_cities)
            
            # Add to closed set
            closed_set.add(current_state)
            
            # Generate possible next legs
            for next_capital, cities_to_visit, distance, flight_time in self.get_possible_legs(current_capital, visited_cities):
                # Create new state
                new_visited = visited_cities.union(cities_to_visit)
                new_state = (next_capital, new_visited)
                
                # Calculate new g score
                tentative_g = g_score[current_state] + 1
                
                # If this is a better path to the state
                if new_state not in g_score or tentative_g < g_score[new_state]:
                    came_from[new_state] = (current_state, distance, flight_time)
                    g_score[new_state] = tentative_g
                    f_score = tentative_g + self.heuristic(new_visited)
                    
                    # Add to open list if not in closed set
                    if new_state not in closed_set:
                        heappush(open_list, (f_score, id(new_state), new_state))
        
        # Reconstruct path
        route = []
        current = best_state
        while current in came_from:
            prev, distance, flight_time = came_from[current]
            current_capital, visited_cities = current
            prev_capital, prev_visited = prev
            cities_visited = visited_cities - prev_visited
            route.append((current_capital, cities_visited, distance, flight_time))
            current = prev
        
        route.reverse()
        return route, best_cities_visited

    def visualize_route(self, route: List[Tuple[str, Set[str], float, timedelta]], output_file: str = 'drone_route.html'):
        """
        Visualize the route on a map.
        
        Args:
            route: List of (capital, cities_visited, distance, flight_time) tuples
            output_file: Output HTML file path
        """
        # Create map centered on Brazil
        m = folium.Map([-14.5931291, -56.6985808], zoom_start=4)
        
        # Add capitals
        for capital, coord in self.capitals.items():
            folium.Marker(
                coord,
                popup=f"Capital: {capital}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add visited cities and draw routes
        for i, (capital, cities_visited, distance, flight_time) in enumerate(route):
            # Add cities
            for city in cities_visited:
                coord = self.flooded_cities[city]
                folium.Marker(
                    coord,
                    popup=f"City: {city}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)
            
            # Draw route line
            if i < len(route) - 1:
                next_capital = route[i + 1][0]
                folium.PolyLine(
                    [self.capitals[capital], self.capitals[next_capital]],
                    color='red',
                    weight=2,
                    opacity=0.8,
                    popup=f"Distance: {distance:.1f}km<br>Flight time: {flight_time}"
                ).add_to(m)
        
        # Save map
        m.save(output_file) 