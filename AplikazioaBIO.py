import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import requests
import json
import time

# Thingsboard zerbitzariaren datuak
IP = "thingsboard.tknika.eus"
access_token = "qFX7HvM45ruavoM0xn1u"

# CSV fitxategia JSON bihurtzeko funtzioa
def convert_csv_to_json():
    # CSV fitxategia aukeratu
    csv_file_path = filedialog.askopenfilename(
        title="Aukeratu CSV fitxategia",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not csv_file_path:
        messagebox.showerror("Errorea", "Ez da fitxategirik hautatu!")
        return
    
    try:
        # CSV fitxategia irakurri Pandas erabiliz
        df = pd.read_csv(csv_file_path, dtype=str)

        # JSON fitxategiaren bidea lortu
        json_file_path = os.path.splitext(csv_file_path)[0] + ".json"
        
        # CSV datuak JSON formatua egokitu
        json_data = format_csv_to_json(df)

        # JSON fitxategian gorde
        with open(json_file_path, 'w') as f:
            json.dump(json_data, f, indent=4)
        
        # Arrakastaren mezu bat erakutsi
        messagebox.showinfo("Arrakasta", f"JSON fitxategia sortu da:\n{json_file_path}")
        update_status("Arrakasta, JSON fitxategia sortu da, orain datu horiek Thingsboard-era igoko dira.")
        
        # Thingsboard-en telemetriak publikatu zatika "ts" atributuaren arabera
        headers = {'Content-Type': 'application/json'}
        url_post = f"https://{IP}/api/v1/{access_token}/telemetry"

        with open(json_file_path, 'r') as f:
            data = json.load(f)

            # Zatitu JSONa 'ts' atributuaren arabera chunk-etan
            chunks = split_by_ts(data)

            # Taula aktualizatu chunk bakoitza erakutsiz
            for idx, chunk in enumerate(chunks):
                update_status(f"\nChunk {idx+1} bidaltzen ari da: {json.dumps(chunk, indent=2)}")
                
                # Bidali chunk-a Thingsboard-era
                response = requests.post(url_post, headers=headers, json=chunk)
                
                if response.status_code == 200:
                    update_status(f"{idx+1}. Zatia arrakastaz bidali da Thingsboard-era!")
                else:
                    messagebox.showerror("Errorea", f"Ezin izan da zati {idx+1} bidali.\nErantzuna: {response.text}")
                    return

                time.sleep(1)  # 1 segundoko atzerapena
        update_status("JSON datu guztiak bidali dira zatika Thingsboard-era!")

    except Exception as e:
        messagebox.showerror("Errorea", f"Ezin izan da CSV fitxategia JSON bihurtu.\nErrorea: {e}")
        convert_button.config(state=tk.NORMAL)  # Aktibatu botoia

def format_csv_to_json(df):
    """Format CSV Data to JSON format required"""
    json_list = []
    
    for _, row in df.iterrows():
        timestamp_str = row.get("ts", "0")  # Timestamp zutabea izenik gabe badago, '0' erabiliko da
        
        # Convert timestamp to integer (if possible)
        try:
            timestamp = int(float(timestamp_str))*1000
        except ValueError:
            timestamp = 0  # Default value if conversion fails

        values = row.drop("ts").to_dict()  # Timestamp ez den gainontzeko datuak
        json_object = {
            "ts": timestamp,
            "values": values
        }
        json_list.append(json_object)
    
    return json_list

def split_by_ts(data):
    """ Telemetria JSON zatiak banatu 'ts' atributuaren arabera """
    chunks = []
    current_chunk = []

    for record in data:
        # 'ts' atributua duen erregistro berria aurkitu
        if "ts" in record:
            # Chunk berria sortu aurrekoa existitzen bada
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
        # Gehitu uneko erregistroa chunk-era
        current_chunk.append(record)
    
    # Gehitu azken chunk-a
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def update_status(message):
    # Status mezuaren testua eguneratu
    status_text.insert(tk.END, message + '\n')
    status_text.yview(tk.END)  # Scrolla azken mezuari
    root.update_idletasks()  # Tkinter GUI-ren eguneratzeak behin-behinean eguneratu

# Interfaze grafikoa sortu
root = tk.Tk()
root.title("CSV to JSON bihurgailua")

# Botoia interfazean
convert_button = tk.Button(root, text="Aukeratu CSV eta bihurtu JSON", command=convert_csv_to_json)
convert_button.pack(pady=10)

# Status mezuaren taula
status_text = tk.Text(root, height=20, width=70, wrap=tk.WORD)
status_text.pack(padx=10, pady=10)

# Tkinter aplikazioa martxan jarri
root.mainloop()










