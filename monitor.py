import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from ping3 import ping
import datetime

# 1. Configuración de servidores (Ubicaciones aproximadas de AWS/GCP)
servers = [
    {"name": "US East (Virginia)", "host": "ec2.us-east-1.amazonaws.com", "lat": 38.03, "lon": -78.47},
    {"name": "US West (California)", "host": "ec2.us-west-1.amazonaws.com", "lat": 37.33, "lon": -121.89},
    {"name": "EU Central (Frankfurt)", "host": "ec2.eu-central-1.amazonaws.com", "lat": 50.11, "lon": 8.68},
    {"name": "Asia Pacific (Tokyo)", "host": "ec2.ap-northeast-1.amazonaws.com", "lat": 35.68, "lon": 139.69},
    {"name": "South America (São Paulo)", "host": "ec2.sa-east-1.amazonaws.com", "lat": -23.55, "lon": -46.63},
    {"name": "Australia (Sydney)", "host": "ec2.ap-southeast-2.amazonaws.com", "lat": -33.86, "lon": 151.20}
]

# 2. Medir Latencia
results = []
print(f"Iniciando test de latencia: {datetime.datetime.now()}")

for server in servers:
    try:
        # Hacemos ping (retorna segundos, convertimos a ms)
        latency = ping(server["host"], unit='ms')
        if latency is None: latency = 0
        server["latency"] = round(latency, 2)
        print(f"{server['name']}: {server['latency']} ms")
    except Exception as e:
        server["latency"] = 0
        print(f"Error en {server['name']}: {e}")
    results.append(server)

# 3. Crear DataFrame y Mapa
df = pd.DataFrame(results)
# Usamos la URL directa del dataset Natural Earth
url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)

# Configurar el gráfico
fig, ax = plt.subplots(figsize=(15, 10))
world.plot(ax=ax, color='#2d2d2d', edgecolor='#444444') # Estilo Dark Mode
fig.patch.set_facecolor('#0d1117') # Fondo estilo GitHub Dark
ax.set_facecolor('#0d1117')

# Mapear latencia a colores y tamaños
# Puntos verdes (rápido) a rojos (lento)
sc = ax.scatter(df['lon'], df['lat'], 
                c=df['latency'], cmap='RdYlGn_r', # Rojo=Alto, Verde=Bajo
                s=df['latency']*5 + 100, # El tamaño depende de la latencia
                alpha=0.8, edgecolors='white', zorder=2)

# Añadir etiquetas con los valores
for x, y, label, val in zip(df['lon'], df['lat'], df['name'], df['latency']):
    ax.text(x + 2, y, f"{val}ms", color='white', fontsize=9, fontweight='bold')

plt.title(f"Global Latency Heatmap - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 
          color='white', fontsize=15)
ax.axis('off')

# Guardar imagen
plt.savefig("latency_map.png", bbox_inches='tight', pad_inches=0.2, dpi=100)
print("Mapa generado exitosamente.")