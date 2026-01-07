"""
Transformation 06: Préparation des Dimensions pour le Data Warehouse
Phase 5.2 - Transformation: Dimensions
Gère le SCD Type 2 pour les dimensions qui changent dans le temps
"""
import csv
import os
from datetime import datetime

def extract_year_from_date(date_str):
    """Extrait l'année d'une date"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
        return date_obj.year
    except:
        return None

def prepare_dim_region():
    """Prépare la dimension région avec SCD Type 2"""
    print("📋 Préparation dim_region...")
    
    input_file = r"D:\BI\03_etl\staging\transformed\regions_enriched.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\dim_region_ready.csv"
    
    rows_written = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_region', 'nom_region', 'pays', 'zone_climatique', 
                     'population', 'superficie_km2', 'date_debut', 'date_fin', 'est_actuel']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Pour SCD Type 2, on crée une version actuelle
                date_debut = row['date_creation'] if row['date_creation'] else '2026-01-01'
                # Extraire juste la date (sans l'heure)
                if ' ' in date_debut:
                    date_debut = date_debut.split(' ')[0]
                
                prepared_row = {
                    'code_region': row['id_region'],
                    'nom_region': row['nom_region'],
                    'pays': row['pays'],
                    'zone_climatique': row['zone_climatique'],
                    'population': int(float(row['population'])) if row['population'] else '',
                    'superficie_km2': float(row['superficie_km2']) if row['superficie_km2'] else '',
                    'date_debut': date_debut,
                    'date_fin': '',  # NULL pour les versions actuelle
                    'est_actuel': 'TRUE'
                }
                writer.writerow(prepared_row)
                rows_written += 1
    
    print(f"  ✓ {rows_written} régions préparées")
    return rows_written

def prepare_dim_batiment():
    """Prépare la dimension bâtiment avec SCD Type 2"""
    print("📋 Préparation dim_batiment...")
    
    input_file = r"D:\BI\03_etl\staging\transformed\batiments_cleaned.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\dim_batiment_ready.csv"
    
    rows_written = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_batiment', 'nom_batiment', 'code_region', 'type_batiment', 
                     'ville', 'surface_m2', 'nombre_etages', 'annee_construction', 
                     'certification_energetique', 'date_debut', 'date_fin', 'est_actuel']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                date_debut = row['date_creation'] if row['date_creation'] else '2026-01-01'
                if ' ' in date_debut:
                    date_debut = date_debut.split(' ')[0]
                
                # Extraire l'année de construction
                annee_construction = extract_year_from_date(row.get('annee_construction', ''))
                
                prepared_row = {
                    'code_batiment': row['id_batiment'],
                    'nom_batiment': row['nom_batiment'],
                    'code_region': row['id_region'],  # On garde le code pour lookup après
                    'type_batiment': row['type_batiment'],
                    'ville': row['ville'],
                    'surface_m2': float(row['surface_m2']) if row['surface_m2'] else '',
                    'nombre_etages': int(float(row['nombre_etages'])) if row['nombre_etages'] else '',
                    'annee_construction': annee_construction if annee_construction else '',
                    'certification_energetique': row['certification_energetique'],
                    'date_debut': date_debut,
                    'date_fin': '',
                    'est_actuel': 'TRUE'
                }
                writer.writerow(prepared_row)
                rows_written += 1
    
    print(f"  ✓ {rows_written} bâtiments préparés")
    return rows_written

def prepare_dim_client():
    """Prépare la dimension client avec SCD Type 2"""
    print("📋 Préparation dim_client...")
    
    input_file = r"D:\BI\03_etl\staging\transformed\clients_cleaned.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\dim_client_ready.csv"
    
    rows_written = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_client', 'type_client', 'nom', 'prenom', 'raison_sociale', 
                     'segment_client', 'ville', 'date_debut', 'date_fin', 'est_actuel']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                date_debut = row['date_creation'] if row['date_creation'] else '2026-01-01'
                if ' ' in date_debut:
                    date_debut = date_debut.split(' ')[0]
                
                prepared_row = {
                    'code_client': row['id_client'],
                    'type_client': row['type_client'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'raison_sociale': row['raison_sociale'],
                    'segment_client': row['segment_client'],
                    'ville': row['ville'],
                    'date_debut': date_debut,
                    'date_fin': '',
                    'est_actuel': 'TRUE'
                }
                writer.writerow(prepared_row)
                rows_written += 1
    
    print(f"  ✓ {rows_written} clients préparés")
    return rows_written

def prepare_dim_compteur():
    """Prépare la dimension compteur avec SCD Type 2"""
    print("📋 Préparation dim_compteur...")
    
    input_file = r"D:\BI\03_etl\staging\extracted\compteurs_extracted.csv.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\dim_compteur_ready.csv"
    
    rows_written = 0
    
    # Essayer différents encodages
    encodings = ['windows-1252', 'latin-1', 'cp1252', 'utf-8']
    file_handle = None
    reader = None
    
    for enc in encodings:
        try:
            file_handle = open(input_file, 'r', encoding=enc, errors='replace')
            reader = csv.DictReader(file_handle, delimiter=';')
            test_row = next(reader)
            file_handle.seek(0)
            reader = csv.DictReader(file_handle, delimiter=';')
            break
        except Exception:
            if file_handle:
                file_handle.close()
            continue
    
    if file_handle is None or reader is None:
        print("  ⚠ Fichier compteurs non trouvé ou illisible, création d'une version basique...")
        # Créer des compteurs basiques depuis les données de consommation
        with open(output_file, 'w', newline='', encoding='utf-8') as out:
            fieldnames = ['code_compteur', 'numero_serie', 'code_batiment', 'code_type_energie', 
                         'marque', 'modele', 'date_installation', 'date_debut', 'date_fin', 'est_actuel']
            writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            # Extraire les compteurs depuis les fichiers de consommation
            compteurs_seen = set()
            consommation_files = [
                r"D:\BI\03_etl\staging\transformed\consommation_eau_enriched.csv",
                r"D:\BI\03_etl\staging\transformed\consommation_elec_enriched.csv",
                r"D:\BI\03_etl\staging\transformed\consommation_gaz_enriched.csv"
            ]
            
            type_energie_map = {
                'EAU_': 'EAU',
                'ELEC_': 'ELEC',
                'GAZ_': 'GAZ'
            }
            
            for file_path in consommation_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cons_reader = csv.DictReader(f, delimiter=';')
                        for row in cons_reader:
                            compteur_id = row.get('compteur_id', '')
                            batiment_id = row.get('id_batiment', '')
                            
                            if compteur_id and (compteur_id, batiment_id) not in compteurs_seen:
                                compteurs_seen.add((compteur_id, batiment_id))
                                
                                # Déterminer le type d'énergie
                                code_type = 'EAU'
                                for prefix, code in type_energie_map.items():
                                    if compteur_id.startswith(prefix):
                                        code_type = code
                                        break
                                
                                prepared_row = {
                                    'code_compteur': compteur_id,
                                    'numero_serie': compteur_id.replace('_', '-'),
                                    'code_batiment': batiment_id,
                                    'code_type_energie': code_type,
                                    'marque': 'GreenTech',
                                    'modele': 'GT-2024',
                                    'date_installation': '2024-01-01',
                                    'date_debut': '2024-01-01',
                                    'date_fin': '',
                                    'est_actuel': 'TRUE'
                                }
                                writer.writerow(prepared_row)
                                rows_written += 1
        
        print(f"  ✓ {rows_written} compteurs préparés (depuis consommation)")
        return rows_written
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as out:
            # Déterminer les colonnes disponibles
            fieldnames_in = reader.fieldnames
            print(f"  Colonnes disponibles: {fieldnames_in}")
            
            # Colonnes de sortie attendues
            fieldnames = ['code_compteur', 'numero_serie', 'code_batiment', 'code_type_energie', 
                         'marque', 'modele', 'date_installation', 'date_debut', 'date_fin', 'est_actuel']
            writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for row in reader:
                # Adapter selon les colonnes disponibles
                code_compteur = row.get('id_compteur') or row.get('code_compteur') or ''
                code_batiment = row.get('id_batiment') or ''
                
                if not code_compteur:
                    continue
                
                # Déterminer type énergie depuis le code
                code_type = 'EAU'
                if 'ELEC' in code_compteur.upper():
                    code_type = 'ELEC'
                elif 'GAZ' in code_compteur.upper():
                    code_type = 'GAZ'
                
                date_installation = row.get('date_installation', '2024-01-01')
                if ' ' in date_installation:
                    date_installation = date_installation.split(' ')[0]
                
                prepared_row = {
                    'code_compteur': code_compteur,
                    'numero_serie': row.get('numero_serie', code_compteur.replace('_', '-')),
                    'code_batiment': code_batiment,
                    'code_type_energie': code_type,
                    'marque': row.get('marque', 'GreenTech'),
                    'modele': row.get('modele', 'GT-2024'),
                    'date_installation': date_installation,
                    'date_debut': date_installation,
                    'date_fin': '',
                    'est_actuel': 'TRUE'
                }
                writer.writerow(prepared_row)
                rows_written += 1
    finally:
        if file_handle:
            file_handle.close()
    
    print(f"  ✓ {rows_written} compteurs préparés")
    return rows_written

def prepare_dim_type_energie():
    """Prépare la dimension type_energie (table fixe)"""
    print("📋 Préparation dim_type_energie...")
    
    output_file = r"D:\BI\03_etl\staging\transformed\dim_type_energie_ready.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['nom_energie', 'unite_mesure', 'facteur_emission_co2', 'categorie']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        # Types d'énergie fixes
        types_energie = [
            {'nom_energie': 'Électricité', 'unite_mesure': 'kWh', 'facteur_emission_co2': 0.4500, 'categorie': 'Énergie'},
            {'nom_energie': 'Eau', 'unite_mesure': 'm3', 'facteur_emission_co2': 0.0003, 'categorie': 'Ressource'},
            {'nom_energie': 'Gaz', 'unite_mesure': 'm3', 'facteur_emission_co2': 2.3500, 'categorie': 'Énergie'}
        ]
        
        for type_energie in types_energie:
            writer.writerow(type_energie)
    
    print(f"  ✓ 3 types d'énergie préparés")
    return 3

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TRANSFORMATION 06 - PRÉPARATION DES DIMENSIONS")
    print("=" * 60)
    print("\n📋 Préparation des dimensions pour le Data Warehouse...")
    print("   Avec gestion SCD Type 2 pour l'historisation\n")
    
    total_rows = 0
    
    # Préparer chaque dimension
    total_rows += prepare_dim_region()
    total_rows += prepare_dim_batiment()
    total_rows += prepare_dim_client()
    total_rows += prepare_dim_compteur()
    total_rows += prepare_dim_type_energie()
    
    print("\n" + "=" * 60)
    print("✅ TRANSFORMATION DIMENSIONS TERMINÉE !")
    print("=" * 60)
    print(f"\n📊 Résumé:")
    print(f"   - Total d'enregistrements préparés: {total_rows}")
    print(f"\n📁 Fichiers créés dans staging/transformed/:")
    print(f"   - dim_region_ready.csv")
    print(f"   - dim_batiment_ready.csv")
    print(f"   - dim_client_ready.csv")
    print(f"   - dim_compteur_ready.csv")
    print(f"   - dim_type_energie_ready.csv")
    print("\n✨ Caractéristiques:")
    print("   ✓ SCD Type 2 implémenté (date_debut, date_fin, est_actuel)")
    print("   ✓ Clés métier préservées (code_*)")
    print("   ✓ Prêt pour chargement dans le DW")

if __name__ == "__main__":
    main()

