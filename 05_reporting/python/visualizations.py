"""
Script de Visualisation - GreenCity BI
Génère des graphiques à partir des données du Data Warehouse
"""
import mysql.connector
import configparser
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Pour éviter les problèmes d'affichage sur Windows
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration des styles
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

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

def create_output_dir():
    """Crée le dossier de sortie pour les graphiques"""
    output_dir = Path(r"D:\BI\05_reporting\visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def save_figure(fig, filename, output_dir):
    """Sauvegarde une figure"""
    filepath = output_dir / filename
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"   ✅ Graphique sauvegardé: {filepath}")
    plt.close(fig)

def visualization_1_consommation_par_type(output_dir, conn):
    """Graphique 1: Consommation par type d'énergie"""
    query = """
    SELECT 
        te.nom_energie AS Type_Energie,
        ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_kWh
    FROM fact_consommation fc
    INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
    GROUP BY te.nom_energie
    ORDER BY SUM(fc.consommation_normalisee) DESC
    """
    
    df = pd.read_sql(query, conn)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df['Type_Energie'], df['Consommation_kWh'], 
                   color=['#2ecc71', '#3498db', '#e74c3c'])
    ax.set_title('Consommation Totale par Type d\'Énergie', fontsize=14, fontweight='bold')
    ax.set_xlabel('Type d\'Énergie', fontsize=12)
    ax.set_ylabel('Consommation (kWh)', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.xticks(rotation=0)
    save_figure(fig, '01_consommation_par_type.png', output_dir)

def visualization_2_top_batiments(output_dir, conn):
    """Graphique 2: Top 10 bâtiments consommateurs"""
    query = """
    SELECT 
        b.nom_batiment AS Batiment,
        ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_kWh
    FROM fact_consommation fc
    INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
    GROUP BY b.id_batiment, b.nom_batiment
    ORDER BY SUM(fc.consommation_normalisee) DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, conn)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(df['Batiment'], df['Consommation_kWh'], color='#3498db')
    ax.set_title('Top 10 des Bâtiments les Plus Consommateurs', fontsize=14, fontweight='bold')
    ax.set_xlabel('Consommation (kWh)', fontsize=12)
    ax.set_ylabel('Bâtiment', fontsize=12)
    ax.grid(axis='x', alpha=0.3)
    
    # Inverser l'ordre pour avoir le plus grand en haut
    ax.invert_yaxis()
    
    save_figure(fig, '02_top_batiments_consommateurs.png', output_dir)

def visualization_3_evolution_mensuelle(output_dir, conn):
    """Graphique 3: Évolution mensuelle de la consommation"""
    query = """
    SELECT 
        dd.periode_mois AS Mois,
        te.nom_energie AS Type_Energie,
        ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_kWh
    FROM fact_consommation fc
    INNER JOIN dim_date dd ON fc.id_date = dd.id_date
    INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
    WHERE dd.annee = 2024
    GROUP BY dd.periode_mois, te.nom_energie
    ORDER BY dd.periode_mois, te.nom_energie
    """
    
    df = pd.read_sql(query, conn)
    
    # Pivoter pour avoir les types d'énergie en colonnes
    df_pivot = df.pivot(index='Mois', columns='Type_Energie', values='Consommation_kWh')
    
    fig, ax = plt.subplots(figsize=(14, 6))
    df_pivot.plot(kind='line', marker='o', ax=ax, linewidth=2, markersize=8)
    ax.set_title('Évolution Mensuelle de la Consommation en 2024', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mois', fontsize=12)
    ax.set_ylabel('Consommation (kWh)', fontsize=12)
    ax.legend(title='Type d\'Énergie', loc='best')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    save_figure(fig, '03_evolution_mensuelle.png', output_dir)

def visualization_4_rentabilite(output_dir, conn):
    """Graphique 4: Vue d'ensemble de la rentabilité"""
    query = """
    SELECT 
        te.nom_energie AS Type_Energie,
        ROUND(SUM(fr.montant_ttc), 2) AS CA_TTC,
        ROUND(SUM(fr.cout_energie), 2) AS Couts,
        ROUND(SUM(fr.marge), 2) AS Marge
    FROM fact_rentabilite fr
    INNER JOIN dim_type_energie te ON fr.id_type_energie = te.id_type_energie
    GROUP BY te.nom_energie
    ORDER BY SUM(fr.montant_ttc) DESC
    """
    
    df = pd.read_sql(query, conn)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(df))
    width = 0.25
    
    ax.bar([i - width for i in x], df['CA_TTC'], width, label='CA TTC', color='#3498db')
    ax.bar(x, df['Couts'], width, label='Coûts', color='#e74c3c')
    ax.bar([i + width for i in x], df['Marge'], width, label='Marge', color='#2ecc71')
    
    ax.set_title('Rentabilité par Type d\'Énergie', fontsize=14, fontweight='bold')
    ax.set_xlabel('Type d\'Énergie', fontsize=12)
    ax.set_ylabel('Montant (€)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df['Type_Energie'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    save_figure(fig, '04_rentabilite_par_type.png', output_dir)

def visualization_5_emissions_co2(output_dir, conn):
    """Graphique 5: Émissions CO2 par région"""
    query = """
    SELECT 
        r.nom_region AS Region,
        ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS Emissions_tonnes
    FROM fact_environnement fe
    INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
    GROUP BY r.id_region, r.nom_region
    ORDER BY SUM(fe.emission_co2_kg) DESC
    LIMIT 10
    """
    
    df = pd.read_sql(query, conn)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(df['Region'], df['Emissions_tonnes'], color='#e67e22')
    ax.set_title('Top 10 Régions par Émissions CO2', fontsize=14, fontweight='bold')
    ax.set_xlabel('Région', fontsize=12)
    ax.set_ylabel('Émissions CO2 (tonnes)', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    
    # Ajouter les valeurs
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)
    
    save_figure(fig, '05_emissions_co2_par_region.png', output_dir)

def visualization_6_tableau_bord(output_dir, conn):
    """Graphique 6: Tableau de bord avec KPIs"""
    # Récupérer les KPIs
    query_kpi = """
    SELECT 
        (SELECT ROUND(SUM(consommation_normalisee), 2) FROM fact_consommation) AS Consommation_Total,
        (SELECT ROUND(SUM(montant_ttc), 2) FROM fact_rentabilite) AS CA_Total,
        (SELECT ROUND(SUM(emission_co2_kg) / 1000, 2) FROM fact_environnement) AS Emissions_Total,
        (SELECT ROUND(AVG(taux_recyclage) * 100, 2) FROM fact_environnement) AS Taux_Recyclage
    """
    
    df_kpi = pd.read_sql(query_kpi, conn)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Tableau de Bord - KPIs Principaux', fontsize=16, fontweight='bold')
    
    kpis = [
        ('Consommation Totale', df_kpi['Consommation_Total'].iloc[0], 'kWh', '#3498db'),
        ('CA Total', df_kpi['CA_Total'].iloc[0], '€', '#2ecc71'),
        ('Émissions CO2', df_kpi['Emissions_Total'].iloc[0], 'tonnes', '#e74c3c'),
        ('Taux Recyclage', df_kpi['Taux_Recyclage'].iloc[0], '%', '#f39c12')
    ]
    
    for idx, (title, value, unit, color) in enumerate(kpis):
        ax = axes[idx // 2, idx % 2]
        ax.text(0.5, 0.6, f'{value:,.0f}', ha='center', va='center', 
                fontsize=32, fontweight='bold', color=color)
        ax.text(0.5, 0.3, title, ha='center', va='center', 
                fontsize=14, fontweight='bold')
        ax.text(0.5, 0.1, unit, ha='center', va='center', 
                fontsize=12, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    save_figure(fig, '06_tableau_bord_kpis.png', output_dir)

def main():
    """Fonction principale"""
    print("=" * 70)
    print("GÉNÉRATION DES VISUALISATIONS - GreenCity BI")
    print("=" * 70)
    
    # Créer le dossier de sortie
    output_dir = create_output_dir()
    print(f"\n📁 Dossier de sortie: {output_dir}")
    
    # Connexion à la base de données
    db_config = get_db_config()
    print(f"📡 Connexion au Data Warehouse...")
    
    try:
        conn = mysql.connector.connect(**db_config)
        print("✅ Connecté au Data Warehouse\n")
        
        # Générer les visualisations
        print("🎨 Génération des graphiques...\n")
        
        visualization_1_consommation_par_type(output_dir, conn)
        visualization_2_top_batiments(output_dir, conn)
        visualization_3_evolution_mensuelle(output_dir, conn)
        visualization_4_rentabilite(output_dir, conn)
        visualization_5_emissions_co2(output_dir, conn)
        visualization_6_tableau_bord(output_dir, conn)
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Toutes les visualisations ont été générées !")
        print("=" * 70)
        print(f"\n📊 Graphiques sauvegardés dans: {output_dir}")
        print("\n💡 Prochaines étapes:")
        print("   1. Ouvrez les images PNG pour voir les graphiques")
        print("   2. Utilisez ces visualisations dans vos rapports")
        print("   3. Personnalisez les graphiques selon vos besoins")
        
    except mysql.connector.Error as err:
        print(f"❌ Erreur MySQL: {err}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


