import pandas as pd

# Carregar o arquivo Excel
file_path = "database/alagamentos.xlsx"
df = pd.read_excel(file_path)

# Visualizar as primeiras linhas para entender a estrutura
df.head()

# Separar a coluna 'localidade' em 'lat' e 'long'
df[['lat', 'long']] = df['localidade'].str.split(',', expand=True).astype(float)

# Remover a coluna 'descricao' e 'localidade'
df_cleaned = df.drop(columns=['descricao', 'localidade'])

# Remover duplicatas com base em lat e long
df_unique = df_cleaned.drop_duplicates(subset=['lat', 'long'])

# Exportar o DataFrame limpo
output_path = "database/alagamentos-filtred.xlsx"
df_unique.to_excel(output_path, index=False)

output_path