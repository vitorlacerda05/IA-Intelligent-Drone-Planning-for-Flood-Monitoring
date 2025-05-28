# Planejamento Inteligente de Drones para Monitoramento de Alagamentos

Este projeto implementa uma solução para o problema de planejamento de rotas de drones para monitoramento de alagamentos em cidades brasileiras, utilizando o algoritmo A* para otimização.

## Descrição do Problema

O problema consiste em planejar a rota de um drone que deve:
- Partir de uma capital brasileira
- Visitar o maior número possível de cidades afetadas por alagamentos
- Respeitar o limite de 750 km de autonomia por trecho
- Pousar em capitais para reabastecimento
- Deslocar-se a uma velocidade constante de 100 km/h

## Estratégia Implementada

### Modelagem do Problema

1. **Espaço de Estados**:
   - Cada estado é representado por uma tupla `(capital_atual, cidades_visitadas)`
   - `capital_atual`: capital onde o drone está atualmente
   - `cidades_visitadas`: conjunto de cidades já visitadas (usando `frozenset` para imutabilidade)

2. **Função Sucessora**:
   - Gera todos os possíveis próximos estados a partir do estado atual
   - Considera todas as capitais possíveis como destino
   - Para cada par de capitais, tenta incluir o máximo de cidades não visitadas que respeitem o limite de 750 km
   - Ordena as cidades por distância para otimizar a busca

3. **Função de Custo (g)**:
   - Representa o número de pernas de voo realizadas
   - Cada perna corresponde a uma parada para reabastecimento
   - Objetivo: minimizar este valor

4. **Função Heurística (h)**:
   - Estima o número de pernas restantes necessárias
   - Baseada no número de cidades não visitadas e uma estimativa de cidades por perna
   - Fórmula: `ceil(cidades_restantes / estimativa_cidades_por_perna)`
   - Valor estimado de 3 cidades por perna (ajustável)

### Algoritmo A*

O algoritmo A* foi escolhido por suas propriedades:
- **Completude**: garante encontrar uma solução se ela existir
- **Otimização**: encontra a solução com menor custo (menos paradas)
- **Eficiência**: usa a heurística para guiar a busca de forma inteligente

A implementação inclui:
- Lista aberta (fila de prioridade) ordenada por f = g + h
- Conjunto fechado para evitar estados repetidos
- Reconstrução do caminho ótimo
- Acompanhamento do melhor estado encontrado

### Otimizações

1. **Seleção de Cidades**:
   - Ordenação por distância para maximizar cidades visitadas
   - Verificação de distância total antes de adicionar cada cidade

2. **Cálculo de Distâncias**:
   - Uso da fórmula de Haversine para cálculos precisos
   - Consideração da curvatura da Terra

3. **Tempo de Voo**:
   - Cálculo baseado na velocidade constante de 100 km/h
   - Inclusão nos dados de rota para análise

## Visualização

A solução inclui uma visualização interativa que mostra:
- Capitais (marcadores vermelhos)
- Cidades visitadas (marcadores azuis)
- Rotas entre capitais (linhas vermelhas)
- Informações de distância e tempo de voo

## Justificativas das Decisões

1. **Uso do A***:
   - Melhor equilíbrio entre completude e eficiência
   - Permite otimização multi-objetivo (maximizar cidades, minimizar paradas)
   - Heurística adaptável para diferentes cenários

2. **Estimativa de Cidades por Perna**:
   - Valor de 3 cidades baseado em análise preliminar dos dados
   - Pode ser ajustado para otimizar diferentes aspectos
   - Afeta diretamente a agressividade da busca

3. **Representação de Estados**:
   - Uso de `frozenset` para garantir imutabilidade
   - Permite comparação eficiente de estados
   - Facilita a detecção de estados repetidos

4. **Cálculo de Distâncias**:
   - Haversine para precisão geográfica
   - Consideração da curvatura da Terra
   - Importante para respeitar o limite de autonomia

## Como Executar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o planejador:
```bash
python run_planner.py
```

3. Visualize os resultados:
- Abra o arquivo `drone_route.html` em um navegador
- Consulte o output do terminal para detalhes da rota

## Análise de Resultados

O algoritmo busca maximizar:
- Número total de cidades visitadas
- Eficiência do percurso (cidades por perna)
- Minimização de paradas para reabastecimento

Os resultados incluem:
- Rota completa com todas as pernas
- Distância total percorrida
- Tempo total de voo
- Média de cidades visitadas por perna 