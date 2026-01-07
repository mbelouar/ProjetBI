"""
Script d'export des tables du Data Warehouse en CSV
Pour utiliser dans Power BI si le connecteur MySQL ne fonctionne pas
"""
import mysql.connector
import configparser
import pandas as pd
from pathlib import Path

def get_db_config():
    """Charge la configuration MySQL"""
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

def export_table_to_csv(table_name, output_dir, conn):
    """Exporte une table en CSV"""
    print(f"  📋 Export de {table_name}...")
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        
        output_file = output_dir / f"{table_name}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"    ✅ {len(df)} lignes exportées → {output_file.name}")
        return True
    except Exception as e:
        print(f"    ❌ Erreur: {e}")
        return False

def main():
    """Exporte toutes les tables nécessaires pour Power BI"""
    print("=" * 70)
    print("EXPORT DES TABLES EN CSV POUR POWER BI")
    print("=" * 70)
    
    # Créer le dossier de sortie
    output_dir = Path(r"D:\BI\05_reporting\powerbi\csv_export")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Dossier de sortie: {output_dir}")
    
    # Connexion à la base de données
    db_config = get_db_config()
    print(f"\n📡 Connexion au Data Warehouse...")
    
    try:
        conn = mysql.connector.connect(**db_config)
        print("✅ Connecté au Data Warehouse\n")
        
        # Liste des tables à exporter
        tables = [
            # Dimensions
            'dim_date',
            'dim_region',
            'dim_batiment',
            'dim_client',
            'dim_compteur',
            'dim_type_energie',
            
            # Faits
            'fact_consommation',
            'fact_rentabilite',
            'fact_environnement',
        ]
        
        print("📊 Export des tables...\n")
        
        exported = []
        failed = []
        
        for table in tables:
            if export_table_to_csv(table, output_dir, conn):
                exported.append(table)
            else:
                failed.append(table)
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ EXPORT TERMINÉ !")
        print("=" * 70)
        print(f"\n📊 Résumé:")
        print(f"   ✅ {len(exported)} tables exportées avec succès")
        if failed:
            print(f"   ❌ {len(failed)} tables en échec: {', '.join(failed)}")
        
        print(f"\n📁 Fichiers CSV créés dans: {output_dir}")
        print("\n💡 Prochaines étapes dans Power BI:")
        print("   1. Obtenir les données → Texte/CSV")
        print("   2. Sélectionner les fichiers CSV depuis ce dossier")
        print("   3. Charger les données dans Power BI")
        print("\n⚠️  Note: Les données seront statiques (pas de temps réel)")
        print("   Pour mettre à jour, réexécutez ce script et rafraîchissez dans Power BI")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erreur MySQL: {err}")
        print("\n💡 Vérifiez:")
        print("   - Que MySQL est démarré")
        print("   - Vos identifiants dans config/database_config.ini")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


