"""
Chargement 09: Chargement fact_consommation dans le Data Warehouse
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

def load_fact_consommation():
    """Charge fact_consommation"""
    print("=" * 60)
    print("CHARGEMENT 09 - FACT_CONSOMMATION")
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
        
        cursor.execute("SELECT id_compteur, code_compteur FROM dim_compteur WHERE est_actuel = TRUE")
        compteurs_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_region, code_region FROM dim_region WHERE est_actuel = TRUE")
        regions_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id_client, code_client FROM dim_client WHERE est_actuel = TRUE")
        clients_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Mapping type énergie
        type_energie_map = {
            'Eau': 'Eau',
            'Électricité': 'Électricité',
            'Gaz': 'Gaz',
            'EAU': 'Eau',
            'ELEC': 'Électricité',
            'GAZ': 'Gaz'
        }
        cursor.execute("SELECT id_type_energie, nom_energie FROM dim_type_energie")
        type_energie_rows = cursor.fetchall()
        type_energie_lookup = {type_energie_map.get(row[1], row[1]): row[0] for row in type_energie_rows}
        
        print(f"  ✓ Lookups chargés: {len(dates_lookup)} dates, {len(batiments_lookup)} bâtiments, {len(compteurs_lookup)} compteurs")
        
        # Charger les données
        input_file = r"D:\BI\03_etl\staging\transformed\fact_consommation_ready.csv"
        
        print(f"\n📋 Chargement de fact_consommation...")
        
        rows_inserted = 0
        rows_skipped = 0
        errors = 0
        batch_size = 1000
        batch = []
        
        sql = """
        INSERT INTO fact_consommation 
        (id_date, id_heure, id_batiment, id_compteur, id_region, id_client, id_type_energie,
         consommation_kwh, consommation_m3, consommation_normalisee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Resolve lookups
                code_date = int(row['code_date']) if row.get('code_date') else None
                id_date = dates_lookup.get(code_date) if code_date else None
                
                id_heure = int(row['code_heure']) if row.get('code_heure') else 0
                id_batiment = batiments_lookup.get(row['code_batiment'])
                id_compteur = compteurs_lookup.get(row['code_compteur'])
                id_region = regions_lookup.get(row['code_region'])
                id_client = clients_lookup.get(row['code_client']) if row.get('code_client') else None
                
                code_type = row['code_type_energie']
                nom_type_normalise = type_energie_map.get(code_type, code_type)
                id_type_energie = type_energie_lookup.get(nom_type_normalise)
                
                # Vérifier que toutes les FK sont valides
                if not all([id_date, id_batiment, id_compteur, id_region, id_type_energie]):
                    errors += 1
                    continue
                
                # Vérifier doublons (basé sur id_date, id_heure, id_compteur)
                cursor.execute("""
                    SELECT COUNT(*) FROM fact_consommation 
                    WHERE id_date = %s AND id_heure = %s AND id_compteur = %s
                """, (id_date, id_heure, id_compteur))
                if cursor.fetchone()[0] > 0:
                    rows_skipped += 1
                    continue
                
                consommation_kwh = float(row['consommation_kwh']) if row.get('consommation_kwh') else None
                consommation_m3 = float(row['consommation_m3']) if row.get('consommation_m3') else None
                consommation_normalisee = float(row['consommation_normalisee']) if row.get('consommation_normalisee') else 0
                
                batch.append((
                    id_date, id_heure, id_batiment, id_compteur, id_region, id_client, id_type_energie,
                    consommation_kwh, consommation_m3, consommation_normalisee
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
    load_fact_consommation()

