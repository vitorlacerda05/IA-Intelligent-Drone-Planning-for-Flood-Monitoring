# Intelligent Drone Planning for Flood Monitoring using AI

[English](#english) | [Português](#português)

## English

### Overview
This project implements an intelligent drone route planning system for monitoring flood-affected cities in Brazil. The system uses a greedy algorithm to optimize drone routes, considering factors such as maximum autonomy, city priorities, and efficient refueling stops.

### Features
- **Intelligent Route Planning**: Optimizes drone routes to maximize coverage of flood-affected cities
- **Autonomous Operation**: Considers drone's maximum range (750km) and refueling requirements
- **Smart Capital Selection**: Automatically determines the best starting capital based on coverage efficiency
- **Interactive Visualization**: Displays routes and city information on an interactive map
- **Detailed Statistics**: Provides comprehensive information about the route, including:
  - Total distance traveled
  - Number of cities visited
  - Number of refueling stops
  - Time estimates
  - Coverage statistics

### Requirements
- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - pandas
  - folium
  - geopy
  - numpy

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/Intelligent-Drone-Planning-for-Flood-Monitoring-using-AI.git
cd Intelligent-Drone-Planning-for-Flood-Monitoring-using-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage
1. Place your flood data CSV file in the project directory
2. Run the main script:
```bash
python main.py
```

The script will:
1. Load and process the flood data
2. Calculate the optimal starting capital
3. Generate the drone route
4. Create an interactive map visualization
5. Save the results as `drone_route.html`

### Output
The program generates an interactive HTML map showing:
- Drone route with color-coded segments
- Visited cities with detailed information
- Non-visited cities
- Refueling stops
- Route statistics and summary

### Project Structure
```
├── main.py              # Main execution script
├── route_planner.py     # Route planning algorithm
├── map_visualizer.py    # Map visualization module
├── data_processor.py    # Data processing utilities
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Português

### Visão Geral
Este projeto implementa um sistema inteligente de planejamento de rotas para drones no monitoramento de cidades afetadas por enchentes no Brasil. O sistema utiliza um algoritmo guloso para otimizar as rotas dos drones, considerando fatores como autonomia máxima, prioridades das cidades e paradas eficientes para reabastecimento.

### Funcionalidades
- **Planejamento Inteligente de Rotas**: Otimiza as rotas dos drones para maximizar a cobertura das cidades afetadas
- **Operação Autônoma**: Considera a autonomia máxima do drone (750km) e necessidades de reabastecimento
- **Seleção Inteligente de Capital**: Determina automaticamente a melhor capital inicial baseada na eficiência de cobertura
- **Visualização Interativa**: Exibe rotas e informações das cidades em um mapa interativo
- **Estatísticas Detalhadas**: Fornece informações abrangentes sobre a rota, incluindo:
  - Distância total percorrida
  - Número de cidades visitadas
  - Número de paradas para reabastecimento
  - Estimativas de tempo
  - Estatísticas de cobertura

### Requisitos
- Python 3.8+
- Pacotes necessários (instale via `pip install -r requirements.txt`):
  - pandas
  - folium
  - geopy
  - numpy

### Instalação
1. Clone o repositório:
```bash
git clone https://github.com/yourusername/Intelligent-Drone-Planning-for-Flood-Monitoring-using-AI.git
cd Intelligent-Drone-Planning-for-Flood-Monitoring-using-AI
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Uso
1. Coloque seu arquivo CSV com dados de enchentes no diretório do projeto
2. Execute o script principal:
```bash
python main.py
```

O script irá:
1. Carregar e processar os dados de enchentes
2. Calcular a capital inicial ótima
3. Gerar a rota do drone
4. Criar uma visualização interativa do mapa
5. Salvar os resultados como `drone_route.html`

### Saída
O programa gera um mapa HTML interativo mostrando:
- Rota do drone com segmentos coloridos
- Cidades visitadas com informações detalhadas
- Cidades não visitadas
- Paradas para reabastecimento
- Estatísticas e resumo da rota

### Estrutura do Projeto
```
├── main.py              # Script principal de execução
├── route_planner.py     # Algoritmo de planejamento de rotas
├── map_visualizer.py    # Módulo de visualização do mapa
├── data_processor.py    # Utilitários de processamento de dados
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
``` 