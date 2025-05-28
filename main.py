import pandas as pd
import folium
from tqdm import tqdm

df = pd.read_excel('alagamentos.xlsx')
df

m = folium.Map([-14.5931291,-56.6985808], zoom_start=4)

df_sample = df.sample(1000)

# Plotando os marcadores no mapa
for index,row in tqdm(df_sample.iterrows(),total=len(df_sample)):
  localidade = row['localidade'].split(',')
  lat = float(localidade[0])
  lng = float(localidade[1])
  text = row['descricao']
  folium.Marker([lat, lng], popup=text).add_to(m)

m.save('mapa_alagamentos.html')