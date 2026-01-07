"""
Transformation 07: Préparation des Tables de Faits pour le Data Warehouse
Phase 5.2 - Transformation: Faits
Fusionne les données et résout les clés étrangères vers les dimensions
"""
import csv
import os
from datetime import datetime

def extract_date_from_string(date_str):
    """Extrait la date depuis un string (format ISO ou avec timestamp)"""
    if not date_str or date_str.strip() == '':
        return None, None, None, None  # date, annee, mois, jour
    
    date_str = date_str.strip()
    
    # Format avec timestamp: 2024-01-01T08:00:00 ou 2024-01-01 00:00:00
    if 'T' in date_str:
        date_part = date_str.split('T')[0]
    elif ' ' in date_str:
        date_part = date_str.split(' ')[0]
    else:
        date_part = date_str
    
    try:
        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
        return date_part, date_obj.year, date_obj.month, date_obj.day
    except:
        return None, None, None, None

def calculate_date_id(annee, mois, jour):
    """Calcule un ID date simple (format: YYYYMMDD)"""
    if annee and mois and jour:
        return int(f"{annee}{mois:02d}{jour:02d}")
    return None

def load_dimension_lookup(file_path, code_field='code_region'):
    """Charge une dimension et crée un dictionnaire de lookup"""
    lookup = {}
    if not os.path.exists(file_path):
        return lookup
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                code = row.get(code_field, '')
                if code:
                    lookup[code] = row
    except Exception as e:
        print(f"  ⚠ Erreur lors du chargement de {file_path}: {e}")
    
    return lookup

def get_client_from_batiment(code_batiment, batiments_lookup, clients_batiments_map):
    """Trouve le client associé à un bâtiment"""
    # Créer un mapping basique depuis les factures
    return clients_batiments_map.get(code_batiment, '')

def normalize_consumption(consommation, type_energie, unite):
    """Convertit la consommation en kWh équivalent"""
    if not consommation or consommation == '':
        return 0
    
    try:
        cons = float(consommation)
        
        # Facteurs de conversion
        if type_energie.lower() in ['eau', 'water'] or unite.lower() == 'm3':
            # Eau: 1 m3 ≈ 0.0003 kWh (très faible)
            return cons * 0.0003
        elif type_energie.lower() in ['gaz', 'gas'] or 'GAZ' in unite.upper():
            # Gaz: 1 m3 de gaz ≈ 10 kWh
            return cons * 10
        elif type_energie.lower() in ['électricité', 'electricite', 'elec'] or unite.lower() == 'kwh':
            # Électricité: déjà en kWh
            return cons
        else:
            return cons
    except:
        return 0

def prepare_fact_consommation():
    """Prépare la table de faits consommation"""
    print("📋 Préparation fact_consommation...")
    
    # Charger les dimensions pour lookup
    print("  Chargement des dimensions...")
    regions_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_region_ready.csv", 'code_region')
    batiments_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_batiment_ready.csv", 'code_batiment')
    compteurs_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_compteur_ready.csv", 'code_compteur')
    type_energie_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_type_energie_ready.csv", 'nom_energie')
    
    # Créer mapping client-bâtiment depuis les factures
    clients_batiments_map = {}
    factures_file = r"D:\BI\03_etl\staging\transformed\factures_enriched.csv"
    if os.path.exists(factures_file):
        with open(factures_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                batiment = row.get('id_batiment', '')
                client = row.get('id_client', '')
                if batiment and client:
                    clients_batiments_map[batiment] = client
    
    output_file = r"D:\BI\03_etl\staging\transformed\fact_consommation_ready.csv"
    
    consommation_files = [
        (r"D:\BI\03_etl\staging\transformed\consommation_eau_enriched.csv", 'Eau'),
        (r"D:\BI\03_etl\staging\transformed\consommation_elec_enriched.csv", 'Électricité'),
        (r"D:\BI\03_etl\staging\transformed\consommation_gaz_enriched.csv", 'Gaz')
    ]
    
    rows_written = 0
    errors = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_date', 'code_heure', 'code_batiment', 'code_compteur', 'code_region', 
                     'code_client', 'code_type_energie', 'consommation_kwh', 'consommation_m3', 
                     'consommation_normalisee', 'date_mesure']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for file_path, type_energie in consommation_files:
            if not os.path.exists(file_path):
                continue
            
            print(f"  Traitement {type_energie}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    code_region = row.get('id_region', '').strip()
                    code_batiment = row.get('id_batiment', '').strip()
                    code_compteur = row.get('compteur_id', '').strip()
                    date_mesure = row.get('date_mesure', '')
                    
                    # Vérifier que les dimensions existent
                    if code_region not in regions_lookup or code_batiment not in batiments_lookup:
                        errors += 1
                        continue
                    
                    # Trouver le client via le bâtiment
                    code_client = get_client_from_batiment(code_batiment, batiments_lookup, clients_batiments_map)
                    
                    # Extraire date et heure
                    date_str, annee, mois, jour = extract_date_from_string(date_mesure)
                    heure = row.get('heure', '')
                    if not heure and 'T' in date_mesure:
                        try:
                            time_part = date_mesure.split('T')[1]
                            heure = int(time_part.split(':')[0])
                        except:
                            heure = ''
                    
                    # Calculer code_date (YYYYMMDD)
                    code_date = calculate_date_id(annee, mois, jour)
                    
                    # Consommation
                    consommation_value = ''
                    consommation_kwh = ''
                    consommation_m3 = ''
                    
                    if type_energie == 'Électricité':
                        consommation_kwh = row.get('consommation_kWh', '') or row.get('consommation_kwh', '')
                        consommation_value = consommation_kwh
                    else:
                        consommation_m3 = row.get('consommation_m3', '')
                        consommation_value = consommation_m3
                    
                    # Normaliser la consommation
                    consommation_normalisee = normalize_consumption(consommation_value, type_energie, row.get('unite', ''))
                    
                    # Map type énergie
                    code_type_energie = type_energie
                    
                    prepared_row = {
                        'code_date': code_date if code_date else '',
                        'code_heure': heure if heure else '',
                        'code_batiment': code_batiment,
                        'code_compteur': code_compteur,
                        'code_region': code_region,
                        'code_client': code_client,
                        'code_type_energie': code_type_energie,
                        'consommation_kwh': consommation_kwh,
                        'consommation_m3': consommation_m3,
                        'consommation_normalisee': round(consommation_normalisee, 4) if consommation_normalisee else '',
                        'date_mesure': date_mesure
                    }
                    writer.writerow(prepared_row)
                    rows_written += 1
    
    print(f"  ✓ {rows_written} lignes préparées, {errors} erreurs (FK invalides)")
    return rows_written

def prepare_fact_rentabilite():
    """Prépare la table de faits rentabilité"""
    print("📋 Préparation fact_rentabilite...")
    
    # Charger les dimensions
    regions_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_region_ready.csv", 'code_region')
    batiments_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_batiment_ready.csv", 'code_batiment')
    clients_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_client_ready.csv", 'code_client')
    
    # Map id_type_energie vers nom
    type_energie_map = {'1': 'Électricité', '2': 'Eau', '3': 'Gaz'}
    
    input_file = r"D:\BI\03_etl\staging\transformed\factures_enriched.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\fact_rentabilite_ready.csv"
    
    rows_written = 0
    errors = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_date_facture', 'code_date_echeance', 'code_date_paiement',
                     'code_batiment', 'code_client', 'code_region', 'code_type_energie',
                     'code_facture', 'consommation_quantite', 'prix_unitaire', 'montant_ht',
                     'montant_tva', 'montant_ttc', 'cout_energie', 'marge', 'taux_marge',
                     'montant_paye', 'montant_restant', 'delai_paiement_jours', 'est_paye', 'est_en_retard']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                code_region = row.get('id_batiment', '').strip()
                code_batiment = row.get('id_batiment', '').strip()
                code_client = row.get('id_client', '').strip()
                
                # Récupérer la région depuis le bâtiment
                batiment = batiments_lookup.get(code_batiment, {})
                code_region = batiment.get('code_region', code_region)
                
                # Vérifier les FK
                if code_region not in regions_lookup or code_batiment not in batiments_lookup or code_client not in clients_lookup:
                    errors += 1
                    continue
                
                # Dates
                date_facture_str, annee_f, mois_f, jour_f = extract_date_from_string(row.get('date_facture', ''))
                date_echeance_str, annee_e, mois_e, jour_e = extract_date_from_string(row.get('date_echeance', ''))
                
                code_date_facture = calculate_date_id(annee_f, mois_f, jour_f)
                code_date_echeance = calculate_date_id(annee_e, mois_e, jour_e)
                code_date_paiement = ''  # Pas de paiements pour l'instant
                
                # Type énergie
                id_type_energie = row.get('id_type_energie', '')
                code_type_energie = type_energie_map.get(id_type_energie, 'Électricité')
                
                # Calculs
                montant_ttc = float(row.get('montant_ttc', 0)) if row.get('montant_ttc') else 0
                montant_paye = 0  # À remplir si on a les paiements
                montant_restant = montant_ttc - montant_paye
                est_paye = 'FALSE' if montant_restant > 0 else 'TRUE'
                delai_paiement_jours = ''  # Pas de paiement pour l'instant
                est_en_retard = 'FALSE'  # À calculer si on a les dates
                
                prepared_row = {
                    'code_date_facture': code_date_facture if code_date_facture else '',
                    'code_date_echeance': code_date_echeance if code_date_echeance else '',
                    'code_date_paiement': code_date_paiement,
                    'code_batiment': code_batiment,
                    'code_client': code_client,
                    'code_region': code_region,
                    'code_type_energie': code_type_energie,
                    'code_facture': row.get('numero_facture', ''),
                    'consommation_quantite': row.get('consommation_quantite', ''),
                    'prix_unitaire': row.get('prix_unitaire', ''),
                    'montant_ht': row.get('montant_ht', ''),
                    'montant_tva': row.get('montant_tva', ''),
                    'montant_ttc': row.get('montant_ttc', ''),
                    'cout_energie': row.get('cout_energie', ''),
                    'marge': row.get('marge', ''),
                    'taux_marge': row.get('taux_marge', ''),
                    'montant_paye': montant_paye,
                    'montant_restant': round(montant_restant, 2),
                    'delai_paiement_jours': delai_paiement_jours,
                    'est_paye': est_paye,
                    'est_en_retard': est_en_retard
                }
                writer.writerow(prepared_row)
                rows_written += 1
    
    print(f"  ✓ {rows_written} lignes préparées, {errors} erreurs (FK invalides)")
    return rows_written

def prepare_fact_environnement():
    """Prépare la table de faits environnement"""
    print("📋 Préparation fact_environnement...")
    
    # Charger les dimensions
    regions_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_region_ready.csv", 'code_region')
    batiments_lookup = load_dimension_lookup(r"D:\BI\03_etl\staging\transformed\dim_batiment_ready.csv", 'code_batiment')
    
    input_file = r"D:\BI\03_etl\staging\transformed\environnement_enriched.csv"
    output_file = r"D:\BI\03_etl\staging\transformed\fact_environnement_ready.csv"
    
    rows_written = 0
    errors = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        fieldnames = ['code_date', 'code_batiment', 'code_region', 'emission_CO2_kg', 
                     'taux_recyclage', 'ratio_co2_consommation']
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                code_region = row.get('id_region', '').strip()
                code_batiment = row.get('id_batiment', '').strip()
                
                # Vérifier les FK
                if code_region not in regions_lookup or code_batiment not in batiments_lookup:
                    errors += 1
                    continue
                
                # Date
                date_rapport = row.get('date_rapport', '')
                date_str, annee, mois, jour = extract_date_from_string(date_rapport)
                code_date = calculate_date_id(annee, mois, jour)
                
                # Calculs
                emission_co2 = float(row.get('emission_CO2_kg', 0)) if row.get('emission_CO2_kg') else 0
                taux_recyclage = float(row.get('taux_recyclage', 0)) if row.get('taux_recyclage') else 0
                
                # Ratio CO2/consommation (simplifié, devrait être calculé avec consommation totale)
                ratio_co2_consommation = round(emission_co2 / 1000, 4) if emission_co2 > 0 else 0
                
                prepared_row = {
                    'code_date': code_date if code_date else '',
                    'code_batiment': code_batiment,
                    'code_region': code_region,
                    'emission_CO2_kg': emission_co2,
                    'taux_recyclage': taux_recyclage,
                    'ratio_co2_consommation': ratio_co2_consommation
                }
                writer.writerow(prepared_row)
                rows_written += 1
    
    print(f"  ✓ {rows_written} lignes préparées, {errors} erreurs (FK invalides)")
    return rows_written

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TRANSFORMATION 07 - PRÉPARATION DES TABLES DE FAITS")
    print("=" * 60)
    print("\n📋 Préparation des tables de faits pour le Data Warehouse...")
    print("   Avec résolution des clés étrangères\n")
    
    total_rows = 0
    
    # Préparer chaque table de faits
    total_rows += prepare_fact_consommation()
    total_rows += prepare_fact_rentabilite()
    total_rows += prepare_fact_environnement()
    
    print("\n" + "=" * 60)
    print("✅ TRANSFORMATION FAITS TERMINÉE !")
    print("=" * 60)
    print(f"\n📊 Résumé:")
    print(f"   - Total d'enregistrements préparés: {total_rows}")
    print(f"\n📁 Fichiers créés dans staging/transformed/:")
    print(f"   - fact_consommation_ready.csv")
    print(f"   - fact_rentabilite_ready.csv")
    print(f"   - fact_environnement_ready.csv")
    print("\n✨ Caractéristiques:")
    print("   ✓ Clés dimensionnelles résolues (codes)")
    print("   ✓ Consommation normalisée (kWh équivalent)")
    print("   ✓ Calculs de marge et ratios")
    print("   ✓ Prêt pour chargement dans le DW")
    print("\n⚠️  Note: Les codes (code_date, code_*) seront convertis en IDs")
    print("    lors du chargement dans le DW via les lookups des dimensions")

if __name__ == "__main__":
    main()

