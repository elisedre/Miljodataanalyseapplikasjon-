import json
import numpy as np
from collections import defaultdict

def calculate_daily_average(data, date_key="Tidspunkt", temp_key="Temperatur"):
    daily_temps = defaultdict(list)
    
    # Organiser temperaturer per dato
    for entry in data:
        date = entry[date_key].split("T")[0] 
        daily_temps[date].append(entry[temp_key])
    
    # Beregn gjennomsnitt per dato
    daily_avg = {date: round(np.mean(temps), 1) for date, temps in daily_temps.items()}
    
    return daily_avg