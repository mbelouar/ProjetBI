"""
Script pour repeupler dim_date correctement
"""
import mysql.connector
import configparser
from datetime import datetime, timedelta

def get_db_config():
    config = configparser.ConfigParser()
    config.read(r'D:\BI\config\database_config.ini')
    return {
        'host': config.get('MYSQL_DW', 'host'),
        'port': config.getint('MYSQL_DW', 'port'),
        'user': config.get('MYSQL_DW', 'user'),
        'password': config.get('MYSQL_DW', 'password'),
        'database': config.get('MYSQL_DW', 'database'),
        'charset': config.get('MYSQL_DW', 'charset', fallback='utf8mb4')
    }

def populate_dim_date():
    print("Peuplement de dim_date...")
    db_config = get_db_config()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Récupérer les dates existantes
    cursor.execute("SELECT id_date FROM dim_date")
    existing_dates = set(row[0] for row in cursor.fetchall())
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2030, 12, 31)
    current_date = start_date
    
    rows_inserted = 0
    rows_skipped = 0
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        id_date = int(current_date.strftime('%Y%m%d'))
        
        # Ignorer si déjà existante
        if id_date in existing_dates:
            rows_skipped += 1
            current_date = current_date + timedelta(days=1)
            continue
        
        jour = current_date.day
        mois = current_date.month
        annee = current_date.year
        trimestre = (mois - 1) // 3 + 1
        semestre = 1 if mois <= 6 else 2
        jour_semaine = current_date.weekday() + 1
        jour_annee = current_date.timetuple().tm_yday
        semaine_annee = current_date.isocalendar()[1]
        est_weekend = 'TRUE' if jour_semaine in [6, 7] else 'FALSE'
        
        nom_mois = current_date.strftime('%B').title()
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        nom_jour_semaine = jours[current_date.weekday()]
        
        periode_mois = current_date.strftime('%Y-%m')
        periode_trimestre = f"{annee}-Q{trimestre}"
        periode_annee = str(annee)
        
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
        current_date = current_date + timedelta(days=1)
        
        if rows_inserted % 1000 == 0:
            conn.commit()
            print(f"  {rows_inserted} dates insérées...")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✓ {rows_inserted} dates insérées, {rows_skipped} déjà existantes")

if __name__ == "__main__":
    populate_dim_date()

