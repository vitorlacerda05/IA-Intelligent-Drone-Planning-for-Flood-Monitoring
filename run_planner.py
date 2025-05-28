from drone_planner import DronePlanner
from datetime import timedelta

def format_timedelta(td: timedelta) -> str:
    """Format timedelta in a human-readable format."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def main():
    # Initialize the drone planner with the data file
    planner = DronePlanner('alagamentos.xlsx')
    
    # Start from Brasília
    start_capital = 'Brasília'
    
    # Find optimal route
    route, total_cities = planner.find_optimal_route(start_capital)
    
    # Print results
    print(f"\nOptimal route found:")
    print(f"Total cities visited: {total_cities}")
    print(f"Number of steps: {len(route)}")
    
    total_distance = 0
    print("\nRoute details:")
    for i, step in enumerate(route, 1):
        tipo, nome, coord, autonomia = step
        if i > 1:
            _, _, prev_coord, _ = route[i-2]
            total_distance += planner.haversine_distance(prev_coord, coord)
        if tipo == "cidade":
            print(f"{i}. Visitou cidade: {nome} (autonomia restante: {autonomia:.1f} km)")
        elif tipo == "reabastecimento":
            print(f"{i}. Reabasteceu em: {nome} (autonomia restaurada para {autonomia:.1f} km)")
    print(f"\nTotal distance: {total_distance:.1f} km")
    print(f"Average cities per step: {total_cities/len(route):.2f}")
    
    # Visualize the route
    planner.visualize_route(route, 'drone_route.html')
    print("\nRoute visualization saved to 'drone_route.html'")

if __name__ == "__main__":
    main() 