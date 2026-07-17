import matplotlib
matplotlib.use('TkAgg')  # Forza l'uso dello stesso motore grafico della GUI
import matplotlib.pyplot as plt

# 1. Definizione delle coordinate delle boe (Tkinter-style: Y cresce verso il basso)
A1 = (15.0, 15.0)  # In alto a sinistra
A2 = (55.0, 15.0)  # In alto a destra
A3 = (35.0, 55.0)  # In basso al centro (perché Y=55 scende)

# 2. Coordinate esatte delle 16 zone geometriche
zone_coords = {
    1: (15.0, 15.0),   # ON A1
    2: (22.0, 15.0),   # NEAR A1 -> DIR A2
    3: (35.0, 15.0),   # MIDDLE A1-A2
    4: (48.0, 15.0),   # NEAR A2 -> DIR A1
    5: (55.0, 15.0),   # ON A2
    6: (52.0, 22.0),   # NEAR A2 -> DIR A3
    7: (45.0, 35.0),   # MIDDLE A2-A3
    8: (39.0, 48.0),   # NEAR A3 -> DIR A2
    9: (35.0, 55.0),   # ON A3
    10: (31.0, 48.0),  # NEAR A3 -> DIR A1
    11: (25.0, 35.0),  # MIDDLE A3-A1
    12: (18.0, 22.0),  # NEAR A1 -> DIR A3
    13: (23.0, 23.0),  # DISTANT A1 -> DIR CENTER
    14: (47.0, 23.0),  # DISTANT A2 -> DIR CENTER
    15: (35.0, 44.0),  # DISTANT A3 -> DIR CENTER
    16: (35.0, 31.0),  # CENTER
}

# Creazione del grafico
plt.figure(figsize=(9, 9))
ax = plt.gca()

# --- IL SEGRETO: RIBALTA L'ASSE Y ---
ax.invert_yaxis()  # Ora 0 è in alto, 70 è in basso!
ax.xaxis.tick_top()  # Sposta l'asse X in alto per simulare perfettamente il Canvas
ax.xaxis.set_label_position('top')

# Sfondo azzurro mare
ax.set_facecolor('#E0F2F1')

# Disegno del triangolo di Posidonia (allarme)
triangle_x = [A1[0], A2[0], A3[0], A1[0]]
triangle_y = [A1[1], A2[1], A3[1], A1[1]]
plt.fill(triangle_x, triangle_y, color='#FFF59D', alpha=0.5, label='Protected Area (Posidonia)')
plt.plot(triangle_x, triangle_y, color='#FBC02D', linestyle='--', linewidth=2)

# Disegno delle Boe
plt.scatter([A1[0], A2[0], A3[0]], [A1[1], A2[1], A3[1]], color='#D32F2F', s=250, zorder=5, label='Buoys (A1, A2, A3)')
for i, name in enumerate(['Buoy A1', 'Buoy A2', 'Buoy A3']):
    coords = [A1, A2, A3][i]
    # Spostiamo il testo leggermente sopra o sotto a seconda della posizione per non sovrapporlo
    offset = -2.5 if name == 'Buoy A3' else 3.0
    plt.text(coords[0], coords[1] + offset, name, fontsize=11, fontweight='bold', ha='center', color='#1A237E', zorder=6)

# Disegno e categorizzazione delle 16 Zone
for zone_id, (x, y) in zone_coords.items():
    if zone_id in [1, 5, 9]:
        color = '#D32F2F'  # Sulle boe
        marker = 'o'
    elif zone_id in [3, 7, 11]:
        color = '#E65100'  # Punti medi (MIDDLE)
        marker = 's'
    elif zone_id == 16:
        color = '#2E7D32'  # Centro perfetto
        marker = 'D'
    else:
        color = '#0288D1'  # Aree di transito (Near/Distant)
        marker = '^'
        
    plt.scatter(x, y, color=color, s=150, edgecolors='black', zorder=4, marker=marker)
    plt.text(x, y - 1.5, f"Z{zone_id}", fontsize=10, fontweight='bold', ha='center', va='center', 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'), zorder=4)

# Configurazione limiti della mappa 70x70
plt.xlim(0, 70)
plt.ylim(70, 0) # Invertito per coerenza con il flip dell'asse
plt.grid(True, linestyle=':', alpha=0.6, color='#90A4AE')

# Label e Titoli
plt.title("Teti - Mapping for k-NN", fontsize=14, fontweight='bold', pad=25)
plt.xlabel("Coordinate X (Meters)", fontsize=11)
plt.ylabel("Coordinate Y (Meters)", fontsize=11)
plt.legend(loc='lower right', framealpha=0.9)

# Salva l'immagine specchiata
plt.savefig('mappa_16_zone_tkinter.png', dpi=300, bbox_inches='tight')
print("Nuova immagine 'mappa_16_zone_tkinter.png' generata!")
plt.show()