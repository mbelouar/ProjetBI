"""
Script d'extraction des régions depuis MySQL
Extrait la table dim_regions vers un fichier CSV
"""
import csv
import os
import mysql.connector
from datetime import datetime

def extract_regions_from_mysql():
    """Extrait les régions depuis MySQL"""
    print("=" * 60)
    print("EXTRACTION RÉGIONS DEPUIS MYSQL")
    print("=" * 60)
    
    # Configuration MySQL
    import configparser
    config = configparser.ConfigParser()
    config.read(r'D:\BI\config\database_config.ini')
    
    db_config = {
        'host': config.get('MYSQL_OPERATIONAL', 'host', fallback='localhost'),
        'port': config.getint('MYSQL_OPERATIONAL', 'port', fallback=3306),
        'user': config.get('MYSQL_OPERATIONAL', 'user', fallback='root'),
        'password': config.get('MYSQL_OPERATIONAL', 'password', fallback=''),
        'database': config.get('MYSQL_OPERATIONAL', 'database', fallback='greencity_operational'),
        'charset': config.get('MYSQL_OPERATIONAL', 'charset', fallback='utf8mb4')
    }
    
    output_file = r"D:\BI\03_etl\staging\extracted\regions_extracted.csv"
    
    try:
        print("\n📡 Connexion à MySQL...")
        print(f"   Host: {db_config['host']}")
        print(f"   Database: {db_config['database']}")
        print(f"   User: {db_config['user']}")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Requête SQL pour extraire les régions
        # Extraction incrémentale basée sur date_modification
        query = """
        SELECT 
            id_region, 
            nom_region, 
            pays, 
            zone_climatique, 
            population, 
            superficie_km2, 
            DATE_FORMAT(date_creation, '%Y-%m-%d %H:%i:%s') as date_creation,
            DATE_FORMAT(date_modification, '%Y-%m-%d %H:%i:%s') as date_modification
        FROM dim_regions
        ORDER BY id_region
        """
        
        print("  Exécution de la requête...")
        cursor.execute(query)
        regions = cursor.fetchall()
        
        print(f"  ✓ {len(regions)} régions trouvées")
        
        # Écrire dans le fichier CSV
        print(f"\n💾 Écriture dans {output_file}...")
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id_region', 'nom_region', 'pays', 'zone_climatique', 
                         'population', 'superficie_km2', 'date_creation', 'date_modification']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for region in regions:
                # Convertir None en chaînes vides pour les valeurs NULL
                row = {
                    'id_region': region['id_region'] or '',
                    'nom_region': region['nom_region'] or '',
                    'pays': region['pays'] or 'Maroc',
                    'zone_climatique': region['zone_climatique'] or '',
                    'population': region['population'] if region['population'] is not None else '',
                    'superficie_km2': region['superficie_km2'] if region['superficie_km2'] is not None else '',
                    'date_creation': region['date_creation'] or '',
                    'date_modification': region['date_modification'] or ''
                }
                writer.writerow(row)
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Extraction terminée !")
        print(f"   - {len(regions)} régions extraites")
        print(f"   - Fichier: {output_file}")
        
        # Afficher un aperçu
        print("\n📋 Aperçu des données:")
        for i, region in enumerate(regions[:5], 1):
            print(f"   {i}. {region['id_region']} - {region['nom_region']} ({region['pays']})")
        if len(regions) > 5:
            print(f"   ... et {len(regions) - 5} autres")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erreur MySQL: {err}")
        print("\n💡 Vérifiez:")
        print("   - Que MySQL est démarré")
        print("   - Que la base de données 'greencity_operational' existe")
        print("   - Que la table 'dim_regions' existe et contient des données")
        print("   - Vos identifiants MySQL")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_regions_from_mysql()

