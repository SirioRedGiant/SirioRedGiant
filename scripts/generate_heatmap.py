import requests
from bs4 import BeautifulSoup
import datetime
import os

USERNAME = "SirioRedGiant"
URL = f"https://github.com/users/{USERNAME}/contributions"

# Palette Colori (Stile GitHub Scuro)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def fetch_contributions():
    print(f"Scaricando i dati da {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Trova tutte le celle del calendario di GitHub
    days = soup.find_all('td', attrs={'data-date': True, 'data-level': True})
    
    contributions = []
    for day in days:
        contributions.append({
            "date": day['data-date'],
            "level": int(day['data-level'])
        })
        
    # Ordina per data per sicurezza
    contributions.sort(key=lambda x: x['date'])
    return contributions

def generate_svg(contributions):
    if not contributions:
        print("Nessun dato trovato!")
        return ""

    # Parametri della griglia
    CELL_SIZE = 11
    GAP = 4
    WEEKS = 53
    DAYS_IN_WEEK = 7
    
    # Calcolo dimensioni totali
    WIDTH = WEEKS * (CELL_SIZE + GAP) + 20
    HEIGHT = DAYS_IN_WEEK * (CELL_SIZE + GAP) + 20
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">',
        '<style>',
        '  .day { animation: reveal 1s ease-out forwards; opacity: 0; transform: translateY(10px); }',
        '  @keyframes reveal { to { opacity: 1; transform: translateY(0); } }',
        '</style>',
        # Sfondo trasparente (che si adatterà al README)
        f'<rect width="100%" height="100%" fill="transparent"/>', 
        '<g transform="translate(10, 10)">'
    ]
    
    # GitHub fa iniziare la settimana di Domenica
    first_date = datetime.datetime.strptime(contributions[0]['date'], "%Y-%m-%d")
    start_day = (first_date.weekday() + 1) % 7
    
    x = 0
    y = start_day
    
    for contrib in contributions:
        level = contrib['level']
        color = PALETTE[level] if level < len(PALETTE) else PALETTE[-1]
        
        # Effetto cascata diagonale (delay basato su X e Y)
        delay = (x + y) * 0.02
        
        rect = f'<rect class="day" x="{x * (CELL_SIZE + GAP)}" y="{y * (CELL_SIZE + GAP)}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="2" style="animation-delay: {delay:.2f}s"/>'
        svg_parts.append(rect)
        
        y += 1
        if y == DAYS_IN_WEEK:
            y = 0
            x += 1
            
    svg_parts.append('</g>')
    svg_parts.append('</svg>')
    
    return "\n".join(svg_parts)

if __name__ == "__main__":
    data = fetch_contributions()
    print(f"Trovati {len(data)} giorni di contributi.")
    
    svg_content = generate_svg(data)
    
    # Salva il file nella root della repository
    with open("contrib-heatmap.svg", "w") as f:
        f.write(svg_content)
    print("Heatmap generata con successo in 'contrib-heatmap.svg'!")
