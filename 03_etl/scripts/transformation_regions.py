"""
Script de transformation des régions (nettoyage et enrichissement)
"""
import csv
import os
from datetime import datetime

def standardize_date(date_str):
    """Standardise les formats de date vers ISO (yyyy-MM-dd)"""
    if not date_str or date_str.strip() == '':
        return ''
    
    date_str = date_str.strip()
    
    # Format avec timestamp: 2025-10-05 00:00:00
    if ' ' in date_str:
        try:
            date_part = date_str.split(' ')[0]
            return date_part
        except:
            pass
    
    # Format ISO déjà correct
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    
    return date_str

def clean_numeric(value):
    """Nettoie et convertit une valeur numérique"""
    if not value or value.strip() == '':
        return ''
    try:
        cleaned = value.strip().replace(',', '.')
        return float(cleaned)
    except:
        return ''

def clean_string(value):
    """Nettoie une chaîne de caractères (trim)"""
    if value is None:
        return ''
    return value.strip()

def transform_regions():
    """Nettoie et enrichit les régions"""
    print("=" * 60)
    print("TRANSFORMATION - RÉGIONS")
    print("=" * 60)
    
    base_dir = r"D:\BI\03_etl\staging"
    extracted_file = os.path.join(base_dir, "extracted", "regions_extracted.csv")
    transformed_file = os.path.join(base_dir, "transformed", "regions_cleaned.csv")
    enriched_file = os.path.join(base_dir, "transformed", "regions_enriched.csv")
    
    # Créer le dossier transformed s'il n'existe pas
    os.makedirs(os.path.join(base_dir, "transformed"), exist_ok=True)
    
    # === ÉTAPE 1: NETTOYAGE ===
    print("\n📋 Étape 1: Nettoyage...")
    seen_ids = set()
    rows_cleaned = 0
    
    with open(transformed_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['id_region', 'nom_region', 'pays', 'zone_climatique', 
                     'population', 'superficie_km2', 'date_creation', 'date_modification']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(extracted_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                id_region = clean_string(row.get('id_region', ''))
                
                if not id_region or id_region in seen_ids:
                    continue
                seen_ids.add(id_region)
                
                cleaned_row = {
                    'id_region': id_region,
                    'nom_region': clean_string(row.get('nom_region', '')) or 'INCONNU',
                    'pays': clean_string(row.get('pays', '')) or 'Maroc',
                    'zone_climatique': clean_string(row.get('zone_climatique', '')),
                    'population': clean_numeric(row.get('population', '')),
                    'superficie_km2': clean_numeric(row.get('superficie_km2', '')),
                    'date_creation': standardize_date(row.get('date_creation', '')),
                    'date_modification': standardize_date(row.get('date_modification', ''))
                }
                writer.writerow(cleaned_row)
                rows_cleaned += 1
    
    print(f"  ✓ {rows_cleaned} régions nettoyées")
    
    # === ÉTAPE 2: ENRICHISSEMENT ===
    print("\n📋 Étape 2: Enrichissement...")
    rows_enriched = 0
    
    with open(enriched_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['id_region', 'nom_region', 'pays', 'zone_climatique', 
                     'population', 'superficie_km2', 'date_creation', 'date_modification',
                     'densite_population', 'est_metropolitaine']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(transformed_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                population = float(row['population']) if row['population'] else 0
                superficie = float(row['superficie_km2']) if row['superficie_km2'] else 0
                
                # Calcul de la densité de population (habitants/km²)
                densite = (population / superficie) if superficie > 0 else 0
                
                # Déterminer si région métropolitaine (population > 1M ou nom_region contient "Casablanca", "Rabat")
                nom_region = row['nom_region'].lower()
                est_metropolitaine = 'Oui' if (population > 1000000 or 
                                               'casablanca' in nom_region or 
                                               'rabat' in nom_region) else 'Non'
                
                enriched_row = {
                    'id_region': row['id_region'],
                    'nom_region': row['nom_region'],
                    'pays': row['pays'],
                    'zone_climatique': row['zone_climatique'],
                    'population': row['population'],
                    'superficie_km2': row['superficie_km2'],
                    'date_creation': row['date_creation'],
                    'date_modification': row['date_modification'],
                    'densite_population': round(densite, 2) if densite > 0 else '',
                    'est_metropolitaine': est_metropolitaine
                }
                writer.writerow(enriched_row)
                rows_enriched += 1
    
    print(f"  ✓ {rows_enriched} régions enrichies")
    
    print("\n" + "=" * 60)
    print("✅ TRANSFORMATION RÉGIONS TERMINÉE !")
    print("=" * 60)
    print(f"\n📁 Fichiers créés:")
    print(f"   - Nettoyé: {transformed_file}")
    print(f"   - Enrichi: {enriched_file}")
    print("\nOpérations effectuées:")
    print("  ✓ Suppression des doublons")
    print("  ✓ Trim des espaces")
    print("  ✓ Standardisation des dates")
    print("  ✓ Calcul de la densité de population")
    print("  ✓ Identification des régions métropolitaines")

if __name__ == "__main__":
    transform_regions()

