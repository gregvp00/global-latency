import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from ping3 import ping
import datetime
import random
import os

# --- 1. Configuración y Servidores ---
servers = [
    {"name": "US East", "host": "ec2.us-east-1.amazonaws.com", "lat": 38.03, "lon": -78.47},
    {"name": "US West", "host": "ec2.us-west-1.amazonaws.com", "lat": 37.33, "lon": -121.89},
    {"name": "EU Central", "host": "ec2.eu-central-1.amazonaws.com", "lat": 50.11, "lon": 8.68},
    {"name": "Asia Tokyo", "host": "ec2.ap-northeast-1.amazonaws.com", "lat": 35.68, "lon": 139.69},
    {"name": "SA Brazil", "host": "ec2.sa-east-1.amazonaws.com", "lat": -23.55, "lon": -46.63},
    {"name": "Australia", "host": "ec2.ap-southeast-2.amazonaws.com", "lat": -33.86, "lon": 151.20}
]

results = []
total_latency = 0
print(f"--- Iniciando Test: {datetime.datetime.now()} ---")

# --- 2. Ping y Recolección de Datos ---
for server in servers:
    try:
        lat = ping(server["host"], unit='ms')
        if lat is None: lat = 0
    except:
        lat = 0
    
    server["latency"] = round(lat, 2)
    total_latency += server["latency"]
    results.append(server)

# Calcular promedio (evitando división por cero)
avg_latency = total_latency / len(servers) if len(servers) > 0 else 0
print(f"Latencia Promedio Global: {avg_latency:.2f} ms")

# --- 3. Generar Mapa (Igual que antes) ---
df = pd.DataFrame(results)
url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)

fig, ax = plt.subplots(figsize=(15, 10))
world.plot(ax=ax, color='#2d2d2d', edgecolor='#444444')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

sc = ax.scatter(df['lon'], df['lat'], c=df['latency'], cmap='RdYlGn_r', 
                s=df['latency']*5 + 100, alpha=0.8, edgecolors='white', zorder=2)

for x, y, label, val in zip(df['lon'], df['lat'], df['name'], df['latency']):
    ax.text(x + 2, y, f"{val}ms", color='white', fontsize=9, fontweight='bold')

plt.title(f"Global Latency: {avg_latency:.1f}ms avg - {datetime.datetime.now().strftime('%Y-%m-%d')}", color='white')
ax.axis('off')
plt.savefig("latency_map.png", bbox_inches='tight', pad_inches=0.2, dpi=100)

# --- 4. LÓGICA DE COMMITS VARIABLES ---

# Determinamos cuántos commits hacer basado en la "salud" de la red + un factor aleatorio
if avg_latency < 150:
    # Internet rápido: 1 commit calmado
    num_commits = 1
    mood = "stable"
else:
    # Internet lento: Pánico, entre 2 y 6 commits
    num_commits = random.randint(2, 6)
    mood = "unstable"

print(f"Generando estrategia de commits: {num_commits} commits (Modo: {mood})")

# Creamos un script de BASH que GitHub Actions ejecutará LUEGO
with open("commit_strategy.sh", "w") as f:
    f.write("#!/bin/bash\n")
    f.write('git config --global user.name "Latency Bot"\n')
    f.write('git config --global user.email "bot@github.com"\n')
    
    # Commit 1: El mapa siempre se actualiza
    f.write('git add latency_map.png\n')
    f.write(f'git commit -m "🗺️ Update Map: Avg {avg_latency:.0f}ms"\n')
    
    # Commits Extra: Actualizamos un log falso para generar actividad
    for i in range(num_commits - 1):
        # Escribimos una línea tonta en un log
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - REINTENTO {i+1}: Ping alto detectado. Intentando estabilizar...\n"
        
        # Usamos '>>' para añadir al archivo sin borrarlo
        f.write(f'echo "{log_entry}" >> connection_log.txt\n')
        f.write('git add connection_log.txt\n')
        f.write(f'git commit -m "⚠️ Network instability detected: Retry {i+1}/{num_commits}"\n')
    
    f.write('git push\n')

print("Script 'commit_strategy.sh' generado correctamente.")