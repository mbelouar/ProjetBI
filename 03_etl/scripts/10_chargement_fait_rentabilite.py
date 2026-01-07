"""
Chargement 10: Chargement fact_rentabilite dans le Data Warehouse
Phase 5.3 - Chargement (L)
"""
import csv
import os
import mysql.connector
import configparser

def get_db_config():
    """Charge la configuration MySQL depuis le fichier de config"""
    config = configparser.ConfigParser()
    config.read(r'D:\BI\config\database_config.ini')
    
    return {
        'host': config.get('MYSQL_DW', 'host', fallback='localhost'),
        'port': config.getint('MYSQL_DW', 'port', fallback=3306),
        'user': config.get('MYSQL_DW', 'user', fallback='root'),
        'password': config.get('MYSQL_DW', 'password', fallback=''),
        'database': config.get('MYSQL_DW', 'database', fallback='greencity_dw'),
        'charset': config.get('MYSQL_DW', 'charset', fallback='utf8mb4')
    }

def load_fact_rentabilite():
    """Charge fact_rentabilite"""
    print("=" * 60)
    print("CHARGEMENT 10 - FACT_RENTABILITE")
    print("=" * 60)
    
    db_config = get_db_config()
    
    try:
        print("\n📡 Connexion au Data Warehouse...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Créer les lookups
        print("  📋 Chargement des lookups...")
        
        cursor.execute("SELECT id_date, id_date FROM dim_date")
        dates_lookup = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_batiment, code_batiment FROM dim_batiment WHERE est_actuel = TRUE")
        batiments_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_client, code_client FROM dim_client WHERE est_actuel = TRUE")
        clients_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_region, code_region FROM dim_region WHERE est_actuel = TRUE")
        regions_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        type_energie_map = {
            'Électricité': 'Électricité',
            'Eau': 'Eau',
            'Gaz': 'Gaz'
        }
        cursor.execute("SELECT id_type_energie, nom_energie FROM dim_type_energie")
        type_energie_rows = cursor.fetchall()
        type_energie_lookup = {type_energie_map.get(row[1], row[1]): row[0] for row in type_energie_rows}
        
        print(f"  ✓ Lookups chargés")
        
        # Charger les données
        input_file = r"D:\BI\03_etl\staging\transformed\fact_rentabilite_ready.csv"
        
        print(f"\n📋 Chargement de fact_rentabilite...")
        
        rows_inserted = 0
        rows_skipped = 0
        errors = 0
        batch_size = 1000
        batch = []
        
        sql = """
        INSERT INTO fact_rentabilite 
        (id_date_facture, id_date_echeance, id_date_paiement, id_batiment, id_client, id_region, id_type_energie,
         code_facture, consommation_quantite, prix_unitaire, montant_ht, montant_tva, montant_ttc,
         cout_energie, marge, taux_marge, montant_paye, montant_restant, delai_paiement_jours, est_paye, est_en_retard)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Resolve lookups
                code_date_facture = int(row['code_date_facture']) if row.get('code_date_facture') else None
                id_date_facture = dates_lookup.get(code_date_facture) if code_date_facture else None
                
                code_date_echeance = int(row['code_date_echeance']) if row.get('code_date_echeance') else None
                id_date_echeance = dates_lookup.get(code_date_echeance) if code_date_echeance else None
                
                id_date_paiement = None  # Pas de paiements pour l'instant
                
                id_batiment = batiments_lookup.get(row['code_batiment'])
                id_client = clients_lookup.get(row['code_client'])
                id_region = regions_lookup.get(row['code_region'])
                
                code_type = row['code_type_energie']
                nom_type_normalise = type_energie_map.get(code_type, code_type)
                id_type_energie = type_energie_lookup.get(nom_type_normalise)
                
                # Vérifier que toutes les FK sont valides
                if not all([id_date_facture, id_batiment, id_client, id_region, id_type_energie]):
                    errors += 1
                    continue
                
                # Vérifier doublons (basé sur code_facture)
                code_facture = row['code_facture']
                cursor.execute("SELECT COUNT(*) FROM fact_rentabilite WHERE code_facture = %s", (code_facture,))
                if cursor.fetchone()[0] > 0:
                    rows_skipped += 1
                    continue
                
                # Valeurs
                consommation_quantite = float(row['consommation_quantite']) if row.get('consommation_quantite') else None
                prix_unitaire = float(row['prix_unitaire']) if row.get('prix_unitaire') else None
                montant_ht = float(row['montant_ht']) if row.get('montant_ht') else None
                montant_tva = float(row['montant_tva']) if row.get('montant_tva') else None
                montant_ttc = float(row['montant_ttc']) if row.get('montant_ttc') else None
                cout_energie = float(row['cout_energie']) if row.get('cout_energie') else None
                marge = float(row['marge']) if row.get('marge') else None
                taux_marge = float(row['taux_marge']) if row.get('taux_marge') else None
                montant_paye = float(row['montant_paye']) if row.get('montant_paye') else 0
                montant_restant = float(row['montant_restant']) if row.get('montant_restant') else montant_ttc
                delai_paiement = int(row['delai_paiement_jours']) if row.get('delai_paiement_jours') else None
                est_paye = row.get('est_paye', 'FALSE') == 'TRUE'
                est_en_retard = row.get('est_en_retard', 'FALSE') == 'TRUE'
                
                batch.append((
                    id_date_facture, id_date_echeance, id_date_paiement, id_batiment, id_client, id_region, id_type_energie,
                    code_facture, consommation_quantite, prix_unitaire, montant_ht, montant_tva, montant_ttc,
                    cout_energie, marge, taux_marge, montant_paye, montant_restant, delai_paiement, est_paye, est_en_retard
                ))
                
                if len(batch) >= batch_size:
                    cursor.executemany(sql, batch)
                    conn.commit()
                    rows_inserted += len(batch)
                    batch = []
        
        # Insérer le reste
        if batch:
            cursor.executemany(sql, batch)
            conn.commit()
            rows_inserted += len(batch)
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Chargement terminé !")
        print(f"   - {rows_inserted} lignes insérées")
        print(f"   - {rows_skipped} doublons ignorés")
        print(f"   - {errors} erreurs (FK invalides)")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erreur MySQL: {err}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_fact_rentabilite()

