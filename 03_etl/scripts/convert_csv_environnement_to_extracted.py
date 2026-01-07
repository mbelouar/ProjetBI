import csv
import os
import glob
from datetime import datetime

def standardize_date(date_str):
    """
    Standardise les formats de date variés vers ISO format (yyyy-MM-dd)
    Formats possibles: 2024-01-31, 31/01/2024, 01/31/2024
    """
    if not date_str or date_str.strip() == '':
        return ''
    
    date_str = date_str.strip()
    
    # Format ISO déjà correct
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    
    # Format DD/MM/YYYY
    if '/' in date_str and len(date_str) == 10:
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                # Vérifier si c'est DD/MM/YYYY ou MM/DD/YYYY
                if int(parts[0]) > 12:  # DD/MM/YYYY
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:  # MM/DD/YYYY
                    month, day, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
    
    # Si aucun format reconnu, retourner tel quel
    return date_str

def convert_csv_environnement_to_extracted():
    input_dir = r"D:\BI\01_operational_sources\csv"
    output_file = r"D:\BI\03_etl\staging\extracted\environnement_extracted.csv"
    
    seen_rows = set()  # Pour détecter les doublons
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id_region', 'id_batiment', 'date_rapport', 'emission_CO2_kg', 'taux_recyclage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        json_files = glob.glob(os.path.join(input_dir, "env_reports_*.csv"))
        
        total_rows = 0
        duplicates = 0
        
        for csv_file in sorted(json_files):
            print(f"Traitement de {os.path.basename(csv_file)}...")
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # Lit avec virgule comme séparateur
                
                for row in reader:
                    # Nettoyer les espaces (trim)
                    id_region = row['id_region'].strip() if row['id_region'] else ''
                    id_batiment = row['id_batiment'].strip() if row['id_batiment'] else ''
                    date_rapport = standardize_date(row['date_rapport'])
                    
                    # Gérer les valeurs manquantes pour emission_CO2_kg
                    emission_co2 = row['emission_CO2_kg'].strip() if row['emission_CO2_kg'] else ''
                    
                    # Taux de recyclage (garder tel quel, peut être vide)
                    taux_recyclage = row['taux_recyclage'].strip() if row['taux_recyclage'] else ''
                    
                    # Créer une clé pour détecter les doublons
                    row_key = (id_region, id_batiment, date_rapport)
                    
                    # Éviter les doublons exacts
                    if row_key in seen_rows:
                        duplicates += 1
                        continue
                    
                    seen_rows.add(row_key)
                    
                    # Écrire la ligne nettoyée
                    output_row = {
                        'id_region': id_region,
                        'id_batiment': id_batiment,
                        'date_rapport': date_rapport,
                        'emission_CO2_kg': emission_co2,
                        'taux_recyclage': taux_recyclage
                    }
                    writer.writerow(output_row)
                    total_rows += 1
        
        print(f"\n✅ Conversion terminée !")
        print(f"   - Fichiers traités: {len(json_files)}")
        print(f"   - Lignes écrites: {total_rows}")
        print(f"   - Doublons supprimés: {duplicates}")
        print(f"   - Fichier généré: environnement_extracted.csv")

if __name__ == "__main__":
    convert_csv_environnement_to_extracted()

