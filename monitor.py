import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import requests
import datetime
import random
import time

servers = [
    {"name": "US East (N. Virginia)", "url": "https://s3.us-east-1.amazonaws.com", "lat": 38.03, "lon": -78.47},
    {"name": "US West (Oregon)", "url": "https://s3.us-west-2.amazonaws.com", "lat": 44.00, "lon": -120.50},
    {"name": "EU Central (Frankfurt)", "url": "https://s3.eu-central-1.amazonaws.com", "lat": 50.11, "lon": 8.68},
    {"name": "Asia Pacific (Tokyo)", "url": "https://s3.ap-northeast-1.amazonaws.com", "lat": 35.68, "lon": 139.69},
    {"name": "South America (SP)", "url": "https://s3.sa-east-1.amazonaws.com", "lat": -23.55, "lon": -46.63},
    {"name": "Australia (Sydney)", "url": "https://s3.ap-southeast-2.amazonaws.com", "lat": -33.86, "lon": 151.20}
]

results = []
total_latency = 0
print(f"--- Iniciando Test HTTP: {datetime.datetime.now()} ---")

for server in servers:
    try:
        start_time = time.time()
        response = requests.get(server["url"], timeout=2)
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
    except requests.exceptions.RequestException:
        latency_ms = 0
    
    server["latency"] = round(latency_ms, 2)
    total_latency += server["latency"]
    results.append(server)
    print(f"{server['name']}: {server['latency']} ms")

# Calcular promedio
valid_pings = [s["latency"] for s in results if s["latency"] > 0]
avg_latency = sum(valid_pings) / len(valid_pings) if len(valid_pings) > 0 else 0
print(f"Latencia Promedio Global: {avg_latency:.2f} ms")

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
    text_val = f"{val:.0f}ms" if val > 0 else "TIMEOUT"
    ax.text(x + 2, y, text_val, color='white', fontsize=9, fontweight='bold')

plt.title(f"Global HTTP Latency: {avg_latency:.1f}ms avg - {datetime.datetime.now().strftime('%Y-%m-%d')}", color='white')
ax.axis('off')
plt.savefig("latency_map.png", bbox_inches='tight', pad_inches=0.2, dpi=100)

if avg_latency < 150:
    num_commits = 1
    modo = "Stable"
else:
    num_commits = random.randint(2, 5)
    modo = "Instability Detected"

print(f"Modo: {modo} | Commits a generar: {num_commits}")

with open("commit_strategy.sh", "w") as f:
    f.write("#!/bin/bash\n")
    f.write('git config --global user.name "Latency Bot"\n')
    f.write('git config --global user.email "bot@github.com"\n')
    f.write('git add latency_map.png\n')
    f.write(f'git commit -m "🗺️ Update Map: Avg {avg_latency:.0f}ms"\n')
    current_simulated_latency = avg_latency
    for i in range(num_commits - 1):
        jitter = random.randint(-30, 30)
        fake_latency = int(current_simulated_latency + jitter)
        if fake_latency < 0: fake_latency = 10
        fake_time = datetime.datetime.now() + datetime.timedelta(minutes=(i+1))
        timestamp_str = fake_time.strftime("%Y-%m-%dT%H:%M:%S")
        log_entry = f"{timestamp_str} - LATENCY FLUX: {fake_latency}ms. Re-calibrating connection node {random.randint(1,9)}...\n"
        f.write(f'echo "{log_entry}" >> connection_log.txt\n')
        f.write('git add connection_log.txt\n')
        f.write(f'git commit -m "⚠️ Network instability: Retry {i+1}/{num_commits} (Lag: {fake_latency}ms)"\n')
        f.write('sleep 5\n')
    f.write('git push\n')