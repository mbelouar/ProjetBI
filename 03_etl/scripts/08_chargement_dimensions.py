"""
Chargement 08: Chargement des Dimensions dans le Data Warehouse
Phase 5.3 - Chargement (L)
Gère l'UPSERT avec SCD Type 2
"""
import csv
import os
import mysql.connector
import configparser
from datetime import datetime

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

def check_dim_date_exists(conn):
    """Vérifie si dim_date est peuplée"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dim_date")
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

def populate_dim_date_if_needed(conn):
    """Peuple dim_date si elle est vide"""
    cursor = conn.cursor()
    
    # Vérifier si déjà peuplée
    cursor.execute("SELECT COUNT(*) FROM dim_date")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("  ✓ dim_date déjà peuplée")
        cursor.close()
        return
    
    print("  📅 Peuplement de dim_date (2020-2030)...")
    
    # Générer les dates de 2020 à 2030
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2030, 12, 31)
    current_date = start_date
    
    rows_inserted = 0
    from datetime import timedelta
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        id_date = int(current_date.strftime('%Y%m%d'))
        
        jour = current_date.day
        mois = current_date.month
        annee = current_date.year
        trimestre = (mois - 1) // 3 + 1
        semestre = 1 if mois <= 6 else 2
        jour_semaine = current_date.weekday() + 1  # 1=Lundi, 7=Dimanche
        jour_annee = current_date.timetuple().tm_yday
        semaine_annee = current_date.isocalendar()[1]
        est_weekend = 'TRUE' if jour_semaine in [6, 7] else 'FALSE'
        
        # Noms
        nom_mois = current_date.strftime('%B').title()
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        nom_jour_semaine = jours[current_date.weekday()]
        
        # Périodes
        periode_mois = current_date.strftime('%Y-%m')
        periode_trimestre = f"{annee}-Q{trimestre}"
        periode_annee = str(annee)
        
        # Saison
        if mois in [12, 1, 2]:
            saison = 'Hiver'
        elif mois in [3, 4, 5]:
            saison = 'Printemps'
        elif mois in [6, 7, 8]:
            saison = 'Été'
        else:
            saison = 'Automne'
        
        sql = """
        INSERT INTO dim_date (
            id_date, date, jour, mois, annee, trimestre, semestre,
            nom_mois, nom_jour_semaine, jour_semaine, jour_annee, semaine_annee,
            est_weekend, est_jour_ferie, periode_mois, periode_trimestre, periode_annee, saison
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        cursor.execute(sql, (
            id_date, date_str, jour, mois, annee, trimestre, semestre,
            nom_mois, nom_jour_semaine, jour_semaine, jour_annee, semaine_annee,
            est_weekend, 'FALSE', periode_mois, periode_trimestre, periode_annee, saison
        ))
        
        rows_inserted += 1
        # Incrémenter correctement la date
        current_date = current_date + timedelta(days=1)
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} dates insérées dans dim_date")

def load_dim_type_energie(conn, file_path):
    """Charge dim_type_energie (simple INSERT)"""
    print("📋 Chargement dim_type_energie...")
    
    cursor = conn.cursor()
    rows_inserted = 0
    rows_updated = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            nom_energie = row['nom_energie']
            unite_mesure = row['unite_mesure']
            facteur_emission_co2 = float(row['facteur_emission_co2']) if row['facteur_emission_co2'] else 0
            categorie = row.get('categorie', 'Énergie')
            
            # Vérifier si existe déjà
            cursor.execute("SELECT id_type_energie FROM dim_type_energie WHERE nom_energie = %s", (nom_energie,))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE
                sql = """
                UPDATE dim_type_energie 
                SET unite_mesure = %s, facteur_emission_co2 = %s, categorie = %s
                WHERE nom_energie = %s
                """
                cursor.execute(sql, (unite_mesure, facteur_emission_co2, categorie, nom_energie))
                rows_updated += 1
            else:
                # INSERT
                sql = """
                INSERT INTO dim_type_energie (nom_energie, unite_mesure, facteur_emission_co2, categorie)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (nom_energie, unite_mesure, facteur_emission_co2, categorie))
                rows_inserted += 1
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} insérées, {rows_updated} mises à jour")

def load_dim_region(conn, file_path):
    """Charge dim_region avec SCD Type 2"""
    print("📋 Chargement dim_region...")
    
    cursor = conn.cursor()
    rows_inserted = 0
    rows_updated = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            code_region = row['code_region']
            nom_region = row['nom_region']
            pays = row['pays']
            zone_climatique = row.get('zone_climatique') or None
            population = int(row['population']) if row.get('population') else None
            superficie_km2 = float(row['superficie_km2']) if row.get('superficie_km2') else None
            date_debut = row['date_debut']
            est_actuel = row.get('est_actuel', 'TRUE') == 'TRUE'
            
            # Vérifier si existe déjà (version actuelle)
            cursor.execute("""
                SELECT id_region FROM dim_region 
                WHERE code_region = %s AND est_actuel = TRUE
            """, (code_region,))
            existing = cursor.fetchone()
            
            if existing:
                # Vérifier si changement
                cursor.execute("""
                    SELECT nom_region, pays, zone_climatique, population, superficie_km2
                    FROM dim_region WHERE id_region = %s
                """, (existing[0],))
                old_values = cursor.fetchone()
                
                if old_values and (old_values[0] != nom_region or old_values[1] != pays or 
                                 old_values[2] != zone_climatique or old_values[3] != population):
                    # SCD Type 2: Clôturer l'ancienne version
                    cursor.execute("""
                        UPDATE dim_region 
                        SET date_fin = %s, est_actuel = FALSE
                        WHERE id_region = %s
                    """, (date_debut, existing[0]))
                    
                    # Insérer nouvelle version
                    sql = """
                    INSERT INTO dim_region 
                    (code_region, nom_region, pays, zone_climatique, population, superficie_km2, date_debut, est_actuel)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                    """
                    cursor.execute(sql, (code_region, nom_region, pays, zone_climatique, population, superficie_km2, date_debut))
                    rows_inserted += 1
                else:
                    # UPDATE simple (pas de changement)
                    sql = """
                    UPDATE dim_region 
                    SET nom_region = %s, pays = %s, zone_climatique = %s, 
                        population = %s, superficie_km2 = %s
                    WHERE code_region = %s AND est_actuel = TRUE
                    """
                    cursor.execute(sql, (nom_region, pays, zone_climatique, population, superficie_km2, code_region))
                    rows_updated += 1
            else:
                # Première insertion
                sql = """
                INSERT INTO dim_region 
                (code_region, nom_region, pays, zone_climatique, population, superficie_km2, date_debut, est_actuel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(sql, (code_region, nom_region, pays, zone_climatique, population, superficie_km2, date_debut))
                rows_inserted += 1
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} insérées, {rows_updated} mises à jour")

def load_dim_batiment(conn, file_path):
    """Charge dim_batiment avec SCD Type 2"""
    print("📋 Chargement dim_batiment...")
    
    cursor = conn.cursor()
    rows_inserted = 0
    rows_updated = 0
    errors = 0
    
    # Créer lookup des régions (code -> id)
    cursor.execute("SELECT id_region, code_region FROM dim_region WHERE est_actuel = TRUE")
    regions_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            code_batiment = row['code_batiment']
            code_region = row['code_region']
            
            # Lookup id_region
            id_region = regions_lookup.get(code_region)
            if not id_region:
                errors += 1
                continue
            
            nom_batiment = row['nom_batiment']
            type_batiment = row['type_batiment']
            ville = row.get('ville') or None
            surface_m2 = float(row['surface_m2']) if row.get('surface_m2') else None
            nombre_etages = int(row['nombre_etages']) if row.get('nombre_etages') else None
            annee_construction = int(row['annee_construction']) if row.get('annee_construction') else None
            certification_energetique = row.get('certification_energetique') or None
            date_debut = row['date_debut']
            
            # Vérifier si existe déjà
            cursor.execute("""
                SELECT id_batiment FROM dim_batiment 
                WHERE code_batiment = %s AND est_actuel = TRUE
            """, (code_batiment,))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE (simplifié - SCD Type 1 pour l'instant)
                sql = """
                UPDATE dim_batiment 
                SET nom_batiment = %s, id_region = %s, type_batiment = %s, ville = %s,
                    surface_m2 = %s, nombre_etages = %s, annee_construction = %s, 
                    certification_energetique = %s
                WHERE code_batiment = %s AND est_actuel = TRUE
                """
                cursor.execute(sql, (nom_batiment, id_region, type_batiment, ville, surface_m2, 
                                   nombre_etages, annee_construction, certification_energetique, code_batiment))
                rows_updated += 1
            else:
                # INSERT
                sql = """
                INSERT INTO dim_batiment 
                (code_batiment, nom_batiment, id_region, type_batiment, ville, surface_m2, 
                 nombre_etages, annee_construction, certification_energetique, date_debut, est_actuel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(sql, (code_batiment, nom_batiment, id_region, type_batiment, ville, 
                                   surface_m2, nombre_etages, annee_construction, certification_energetique, date_debut))
                rows_inserted += 1
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} insérées, {rows_updated} mises à jour, {errors} erreurs (FK invalides)")

def load_dim_client(conn, file_path):
    """Charge dim_client avec SCD Type 2"""
    print("📋 Chargement dim_client...")
    
    cursor = conn.cursor()
    rows_inserted = 0
    rows_updated = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            code_client = row['code_client']
            type_client = row['type_client']
            nom = row['nom']
            prenom = row.get('prenom') or None
            raison_sociale = row.get('raison_sociale') or None
            segment_client = row.get('segment_client') or None
            ville = row.get('ville') or None
            date_debut = row['date_debut']
            
            # Vérifier si existe déjà
            cursor.execute("""
                SELECT id_client FROM dim_client 
                WHERE code_client = %s AND est_actuel = TRUE
            """, (code_client,))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE
                sql = """
                UPDATE dim_client 
                SET type_client = %s, nom = %s, prenom = %s, raison_sociale = %s,
                    segment_client = %s, ville = %s
                WHERE code_client = %s AND est_actuel = TRUE
                """
                cursor.execute(sql, (type_client, nom, prenom, raison_sociale, segment_client, ville, code_client))
                rows_updated += 1
            else:
                # INSERT
                sql = """
                INSERT INTO dim_client 
                (code_client, type_client, nom, prenom, raison_sociale, segment_client, ville, date_debut, est_actuel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(sql, (code_client, type_client, nom, prenom, raison_sociale, segment_client, ville, date_debut))
                rows_inserted += 1
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} insérées, {rows_updated} mises à jour")

def load_dim_compteur(conn, file_path):
    """Charge dim_compteur avec SCD Type 2"""
    print("📋 Chargement dim_compteur...")
    
    cursor = conn.cursor()
    rows_inserted = 0
    rows_updated = 0
    errors = 0
    
    # Lookups
    cursor.execute("SELECT id_batiment, code_batiment FROM dim_batiment WHERE est_actuel = TRUE")
    batiments_lookup = {row[1]: row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id_type_energie, nom_energie FROM dim_type_energie")
    type_energie_rows = cursor.fetchall()
    type_energie_lookup = {row[1]: row[0] for row in type_energie_rows}
    
    # Mapping supplémentaire pour les codes (codes CSV -> noms dans DW)
    type_energie_map = {
        'EAU': 'Eau',
        'ELEC': 'Électricité',
        'GAZ': 'Gaz',
        'Eau': 'Eau',
        'Électricité': 'Électricité',
        'Gaz': 'Gaz',
        'eau': 'Eau',
        'elec': 'Électricité',
        'gaz': 'Gaz'
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            code_compteur = row['code_compteur'].strip() if row.get('code_compteur') else ''
            code_batiment = row['code_batiment'].strip() if row.get('code_batiment') else ''
            code_type_energie = row['code_type_energie'].strip() if row.get('code_type_energie') else ''
            
            if not code_compteur or not code_batiment:
                errors += 1
                continue
            
            # Lookups
            id_batiment = batiments_lookup.get(code_batiment)
            
            # Normaliser le nom du type d'énergie (mapping EAU -> Eau, ELEC -> Électricité, GAZ -> Gaz)
            nom_type_normalise = type_energie_map.get(code_type_energie, code_type_energie)
            id_type_energie = type_energie_lookup.get(nom_type_normalise)
            
            if not id_batiment:
                errors += 1
                continue
            
            if not id_type_energie:
                # Debug: afficher les premiers cas d'erreur
                if errors < 3:
                    print(f"    Erreur: type_energie '{code_type_energie}' -> '{nom_type_normalise}' non trouvé. Types disponibles: {list(type_energie_lookup.keys())}")
                errors += 1
                continue
            
            numero_serie = row.get('numero_serie') or None
            marque = row.get('marque') or None
            modele = row.get('modele') or None
            date_installation = row.get('date_installation') or None
            if date_installation and ' ' in date_installation:
                date_installation = date_installation.split(' ')[0]
            date_debut = row.get('date_debut') or date_installation or '2024-01-01'
            
            # Vérifier si existe déjà
            cursor.execute("""
                SELECT id_compteur FROM dim_compteur 
                WHERE code_compteur = %s AND est_actuel = TRUE
            """, (code_compteur,))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE
                sql = """
                UPDATE dim_compteur 
                SET id_batiment = %s, id_type_energie = %s, numero_serie = %s,
                    marque = %s, modele = %s, date_installation = %s
                WHERE code_compteur = %s AND est_actuel = TRUE
                """
                cursor.execute(sql, (id_batiment, id_type_energie, numero_serie, marque, modele, date_installation, code_compteur))
                rows_updated += 1
            else:
                # INSERT
                sql = """
                INSERT INTO dim_compteur 
                (code_compteur, numero_serie, id_batiment, id_type_energie, marque, modele, date_installation, date_debut, est_actuel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """
                cursor.execute(sql, (code_compteur, numero_serie, id_batiment, id_type_energie, marque, modele, date_installation, date_debut))
                rows_inserted += 1
    
    conn.commit()
    cursor.close()
    print(f"  ✓ {rows_inserted} insérées, {rows_updated} mises à jour, {errors} erreurs (FK invalides)")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("CHARGEMENT 08 - DIMENSIONS DANS LE DATA WAREHOUSE")
    print("=" * 60)
    
    # Configuration
    db_config = get_db_config()
    
    try:
        print("\n📡 Connexion au Data Warehouse...")
        print(f"   Host: {db_config['host']}")
        print(f"   Database: {db_config['database']}")
        
        conn = mysql.connector.connect(**db_config)
        
        # Peupler dim_date si nécessaire
        populate_dim_date_if_needed(conn)
        
        print("\n📋 Chargement des dimensions (ordre respectant les FK)...\n")
        
        # Ordre de chargement (respect des FK)
        base_dir = r"D:\BI\03_etl\staging\transformed"
        
        # 1. dim_type_energie (pas de FK)
        load_dim_type_energie(conn, os.path.join(base_dir, "dim_type_energie_ready.csv"))
        
        # 2. dim_region (pas de FK)
        load_dim_region(conn, os.path.join(base_dir, "dim_region_ready.csv"))
        
        # 3. dim_batiment (FK: id_region)
        load_dim_batiment(conn, os.path.join(base_dir, "dim_batiment_ready.csv"))
        
        # 4. dim_client (pas de FK)
        load_dim_client(conn, os.path.join(base_dir, "dim_client_ready.csv"))
        
        # 5. dim_compteur (FK: id_batiment, id_type_energie)
        load_dim_compteur(conn, os.path.join(base_dir, "dim_compteur_ready.csv"))
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ CHARGEMENT DIMENSIONS TERMINÉ !")
        print("=" * 60)
        print("\n✨ Toutes les dimensions sont chargées dans le DW")
        print("   Prêt pour le chargement des tables de faits")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erreur MySQL: {err}")
        print("\n💡 Vérifiez:")
        print("   - Que MySQL est démarré")
        print("   - Que la base de données 'greencity_dw' existe")
        print("   - Que les tables sont créées (exécuter 01_create_datawarehouse.sql)")
        print("   - Vos identifiants MySQL")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

