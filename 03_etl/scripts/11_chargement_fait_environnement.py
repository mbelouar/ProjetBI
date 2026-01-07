"""
Chargement 11: Chargement fact_environnement dans le Data Warehouse
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

def load_fact_environnement():
    """Charge fact_environnement"""
    print("=" * 60)
    print("CHARGEMENT 11 - FACT_ENVIRONNEMENT")
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
        
        cursor.execute("SELECT id_region, code_region FROM dim_region WHERE est_actuel = TRUE")
        regions_lookup = {row[1]: row[0] for row in cursor.fetchall()}
        
        print(f"  ✓ Lookups chargés")
        
        # Charger les données
        input_file = r"D:\BI\03_etl\staging\transformed\fact_environnement_ready.csv"
        
        print(f"\n📋 Chargement de fact_environnement...")
        
        rows_inserted = 0
        rows_skipped = 0
        errors = 0
        batch_size = 1000
        batch = []
        
        sql = """
        INSERT INTO fact_environnement 
        (id_date, id_batiment, id_region, emission_co2_kg, taux_recyclage, ratio_co2_consommation)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Resolve lookups
                code_date_str = row.get('code_date', '').strip()
                code_date = int(code_date_str) if code_date_str else None
                # id_date = code_date (car dim_date.id_date = format YYYYMMDD)
                id_date = code_date if code_date and code_date in dates_lookup else None
                
                code_batiment = row.get('code_batiment', '').strip()
                code_region = row.get('code_region', '').strip()
                
                id_batiment = batiments_lookup.get(code_batiment)
                id_region = regions_lookup.get(code_region)
                
                # Debug pour les premiers cas d'erreur
                if errors < 5 and not all([id_date, id_batiment, id_region]):
                    missing = []
                    if not id_date:
                        missing.append(f"date={code_date}")
                    if not id_batiment:
                        missing.append(f"batiment={code_batiment}")
                    if not id_region:
                        missing.append(f"region={code_region}")
                    print(f"  Erreur ligne: {', '.join(missing)}")
                
                # Vérifier que toutes les FK sont valides
                if not all([id_date, id_batiment, id_region]):
                    errors += 1
                    continue
                
                # Vérifier doublons (basé sur id_date et id_batiment - UNIQUE KEY)
                cursor.execute("""
                    SELECT COUNT(*) FROM fact_environnement 
                    WHERE id_date = %s AND id_batiment = %s
                """, (id_date, id_batiment))
                if cursor.fetchone()[0] > 0:
                    rows_skipped += 1
                    continue
                
                # Valeurs
                emission_co2 = float(row['emission_CO2_kg']) if row.get('emission_CO2_kg') else None
                taux_recyclage = float(row['taux_recyclage']) if row.get('taux_recyclage') else None
                ratio_co2 = float(row['ratio_co2_consommation']) if row.get('ratio_co2_consommation') else None
                
                batch.append((
                    id_date, id_batiment, id_region, emission_co2, taux_recyclage, ratio_co2
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
    load_fact_environnement()

