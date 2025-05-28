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
    print(f"Number of legs: {len(route)}")
    
    total_distance = 0
    total_time = timedelta()
    
    print("\nRoute details:")
    for i, (capital, cities, distance, flight_time) in enumerate(route, 1):
        total_distance += distance
        total_time += flight_time
        
        print(f"\nLeg {i}:")
        print(f"From: {capital}")
        print(f"Distance: {distance:.1f} km")
        print(f"Flight time: {format_timedelta(flight_time)}")
        print(f"Cities visited: {len(cities)}")
        for city in cities:
            print(f"  - {city}")
    
    print(f"\nTotal distance: {total_distance:.1f} km")
    print(f"Total flight time: {format_timedelta(total_time)}")
    print(f"Average cities per leg: {total_cities/len(route):.1f}")
    
    # Visualize the route
    planner.visualize_route(route, 'drone_route.html')
    print("\nRoute visualization saved to 'drone_route.html'")

if __name__ == "__main__":
    main() 