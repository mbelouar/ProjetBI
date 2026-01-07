"""
Script de Test des Requêtes SQL - GreenCity BI
Teste les requêtes et affiche les résultats
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

def execute_query(query, description):
    """Exécute une requête SQL et retourne un DataFrame"""
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print(f"{'='*60}")
    
    db_config = get_db_config()
    conn = mysql.connector.connect(**db_config)
    
    try:
        df = pd.read_sql(query, conn)
        print(f"\n✅ Résultat: {len(df)} lignes")
        print("\n📋 Aperçu des données:")
        print(df.head(10).to_string(index=False))
        if len(df) > 10:
            print(f"\n... et {len(df) - 10} autres lignes")
        return df
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        conn.close()

def main():
    """Teste quelques requêtes principales"""
    
    print("=" * 70)
    print("TEST DES REQUÊTES SQL - GreenCity BI")
    print("=" * 70)
    
    # Test 1: Vue d'ensemble consommation
    query1 = """
    SELECT 
        te.nom_energie AS Type_Energie,
        COUNT(*) AS Nb_Mesures,
        ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_Totale_kWh,
        ROUND(AVG(fc.consommation_normalisee), 2) AS Moyenne_kWh
    FROM fact_consommation fc
    INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
    GROUP BY te.nom_energie
    ORDER BY SUM(fc.consommation_normalisee) DESC
    """
    df1 = execute_query(query1, "Vue d'ensemble de la consommation par type d'énergie")
    
    # Test 2: Top 5 bâtiments consommateurs
    query2 = """
    SELECT 
        b.nom_batiment AS Batiment,
        b.type_batiment AS Type,
        r.nom_region AS Region,
        ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_Totale_kWh
    FROM fact_consommation fc
    INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
    INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
    GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region
    ORDER BY SUM(fc.consommation_normalisee) DESC
    LIMIT 5
    """
    df2 = execute_query(query2, "Top 5 des bâtiments les plus consommateurs")
    
    # Test 3: Vue d'ensemble rentabilité
    query3 = """
    SELECT 
        te.nom_energie AS Type_Energie,
        COUNT(DISTINCT fr.code_facture) AS Nb_Factures,
        ROUND(SUM(fr.montant_ttc), 2) AS CA_TTC,
        ROUND(SUM(fr.marge), 2) AS Marge_Total,
        ROUND(AVG(fr.taux_marge), 2) AS Taux_Marge_Moyen
    FROM fact_rentabilite fr
    INNER JOIN dim_type_energie te ON fr.id_type_energie = te.id_type_energie
    GROUP BY te.nom_energie
    ORDER BY SUM(fr.montant_ttc) DESC
    """
    df3 = execute_query(query3, "Vue d'ensemble de la rentabilité par type d'énergie")
    
    # Test 4: Émissions CO2 par région
    query4 = """
    SELECT 
        r.nom_region AS Region,
        COUNT(*) AS Nb_Rapports,
        ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS Emissions_CO2_tonnes,
        ROUND(AVG(fe.taux_recyclage) * 100, 2) AS Taux_Recyclage_Moyen
    FROM fact_environnement fe
    INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
    GROUP BY r.id_region, r.nom_region
    ORDER BY SUM(fe.emission_co2_kg) DESC
    LIMIT 5
    """
    df4 = execute_query(query4, "Top 5 régions par émissions CO2")
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés !")
    print("=" * 70)
    print("\n💡 Prochaines étapes:")
    print("   1. Utilisez ces requêtes dans un outil de visualisation")
    print("   2. Consultez les fichiers SQL dans 05_reporting/sql/")
    print("   3. Créez des graphiques avec le script visualizations.py")

if __name__ == "__main__":
    main()


