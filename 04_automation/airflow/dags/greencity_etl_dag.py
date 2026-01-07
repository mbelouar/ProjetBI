#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
DAG Apache Airflow pour l'ETL GreenCity
============================================================================
Auteur: Équipe BI GreenCity
Date: Janvier 2026
Description: Orchestration du processus ETL quotidien
             Exécution: Tous les jours à 02:00
============================================================================
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import os

# Configuration par défaut
default_args = {
    'owner': 'greencity',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email': ['admin@greencity.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Chemins
PENTAHO_HOME = os.getenv('PENTAHO_HOME', '/opt/pentaho/data-integration')
PROJECT_HOME = '/Users/mohammedbelouarraq/Desktop/BI'
ETL_DIR = f'{PROJECT_HOME}/03_etl/pentaho'
LOG_DIR = f'{PROJECT_HOME}/logs'

# Définition du DAG
dag = DAG(
    'greencity_etl_daily',
    default_args=default_args,
    description='ETL quotidien GreenCity - Extraction, Transformation, Chargement',
    schedule_interval='0 2 * * *',  # Tous les jours à 2h00
    catchup=False,
    tags=['greencity', 'etl', 'daily'],
)

# Fonctions Python
def check_prerequisites():
    """Vérifier les prérequis avant l'exécution"""
    import mysql.connector
    from pathlib import Path
    
    print("Vérification des prérequis...")
    
    # Vérifier la connexion MySQL opérationnelle
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password',
            database='greencity_operational'
        )
        conn.close()
        print("✓ Connexion MySQL opérationnelle OK")
    except Exception as e:
        raise Exception(f"Erreur connexion MySQL opérationnelle: {e}")
    
    # Vérifier la connexion MySQL DW
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password',
            database='greencity_dw'
        )
        conn.close()
        print("✓ Connexion MySQL Data Warehouse OK")
    except Exception as e:
        raise Exception(f"Erreur connexion MySQL DW: {e}")
    
    # Vérifier l'existence des fichiers sources
    json_dir = Path(f'{PROJECT_HOME}/01_operational_sources/json')
    csv_dir = Path(f'{PROJECT_HOME}/01_operational_sources/csv')
    
    if not json_dir.exists():
        raise Exception(f"Répertoire JSON introuvable: {json_dir}")
    if not csv_dir.exists():
        raise Exception(f"Répertoire CSV introuvable: {csv_dir}")
    
    print("✓ Répertoires sources OK")
    print("✓ Tous les prérequis sont satisfaits")

def generate_etl_report():
    """Générer un rapport d'exécution ETL"""
    import mysql.connector
    from datetime import datetime
    
    print("Génération du rapport ETL...")
    
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='greencity_dw'
    )
    cursor = conn.cursor(dictionary=True)
    
    # Récupérer les statistiques du dernier ETL
    cursor.execute("""
        SELECT 
            nom_job,
            date_debut,
            date_fin,
            duree_secondes,
            statut,
            nombre_lignes_lues,
            nombre_lignes_ecrites,
            nombre_lignes_rejetees
        FROM etl_log
        WHERE DATE(date_debut) = CURDATE()
        ORDER BY date_debut DESC
        LIMIT 10
    """)
    
    logs = cursor.fetchall()
    
    # Récupérer les statistiques des tables de faits
    cursor.execute("""
        SELECT 
            'fact_consommation' AS table_name,
            COUNT(*) AS nb_lignes,
            MAX(date_ajout) AS derniere_maj
        FROM fact_consommation
        UNION ALL
        SELECT 
            'fact_rentabilite',
            COUNT(*),
            MAX(date_ajout)
        FROM fact_rentabilite
        UNION ALL
        SELECT 
            'fact_environnement',
            COUNT(*),
            MAX(date_ajout)
        FROM fact_environnement
    """)
    
    stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Créer le rapport
    report = f"""
    ========================================
    RAPPORT ETL GREENCITY
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ========================================
    
    LOGS D'EXÉCUTION:
    """
    
    for log in logs:
        report += f"""
    - Job: {log['nom_job']}
      Statut: {log['statut']}
      Durée: {log['duree_secondes']}s
      Lignes lues: {log['nombre_lignes_lues']}
      Lignes écrites: {log['nombre_lignes_ecrites']}
      Lignes rejetées: {log['nombre_lignes_rejetees']}
    """
    
    report += """
    
    STATISTIQUES DES TABLES:
    """
    
    for stat in stats:
        report += f"""
    - {stat['table_name']}: {stat['nb_lignes']} lignes
      Dernière MAJ: {stat['derniere_maj']}
    """
    
    # Sauvegarder le rapport
    report_file = f"{LOG_DIR}/etl_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✓ Rapport sauvegardé: {report_file}")
    print(report)

# ============================================================================
# TÂCHES AIRFLOW
# ============================================================================

# Tâche 0: Vérification des prérequis
task_check_prerequisites = PythonOperator(
    task_id='check_prerequisites',
    python_callable=check_prerequisites,
    dag=dag,
)

# Tâche 1: Extraction depuis MySQL
task_extract_mysql = BashOperator(
    task_id='extract_mysql',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/01_extraction_mysql.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 2: Extraction depuis JSON
task_extract_json = BashOperator(
    task_id='extract_json',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/02_extraction_json.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 3: Extraction depuis CSV
task_extract_csv = BashOperator(
    task_id='extract_csv',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/03_extraction_csv.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 4: Transformation - Nettoyage
task_transform_cleaning = BashOperator(
    task_id='transform_cleaning',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/04_transformation_nettoyage.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 5: Transformation - Enrichissement
task_transform_enrichment = BashOperator(
    task_id='transform_enrichment',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/05_transformation_enrichissement.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 6: Transformation - Dimensions
task_transform_dimensions = BashOperator(
    task_id='transform_dimensions',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/06_transformation_dimensions.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 7: Transformation - Faits
task_transform_facts = BashOperator(
    task_id='transform_facts',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/07_transformation_faits.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 8: Chargement - Dimensions
task_load_dimensions = BashOperator(
    task_id='load_dimensions',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/08_chargement_dimensions.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 9: Chargement - Fait Consommation
task_load_fact_consommation = BashOperator(
    task_id='load_fact_consommation',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/09_chargement_fait_consommation.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 10: Chargement - Fait Rentabilité
task_load_fact_rentabilite = BashOperator(
    task_id='load_fact_rentabilite',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/10_chargement_fait_rentabilite.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 11: Chargement - Fait Environnement
task_load_fact_environnement = BashOperator(
    task_id='load_fact_environnement',
    bash_command=f'{PENTAHO_HOME}/pan.sh -file={ETL_DIR}/transformations/11_chargement_fait_environnement.ktr -level=Basic >> {LOG_DIR}/etl_$(date +%Y%m%d).log 2>&1',
    dag=dag,
)

# Tâche 12: Génération du rapport
task_generate_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_etl_report,
    dag=dag,
)

# Tâche 13: Notification par email (succès)
task_email_success = EmailOperator(
    task_id='email_success',
    to='admin@greencity.com',
    subject='[GreenCity ETL] Exécution réussie - {{ ds }}',
    html_content="""
    <h3>ETL GreenCity - Exécution réussie</h3>
    <p>Date: {{ ds }}</p>
    <p>L'ETL quotidien s'est terminé avec succès.</p>
    <p>Consultez le rapport détaillé dans le répertoire logs.</p>
    """,
    dag=dag,
)

# ============================================================================
# DÉFINITION DES DÉPENDANCES
# ============================================================================

# Phase 0: Prérequis
task_check_prerequisites

# Phase 1: Extraction (en parallèle)
task_check_prerequisites >> [task_extract_mysql, task_extract_json, task_extract_csv]

# Phase 2: Transformation (séquentiel)
[task_extract_mysql, task_extract_json, task_extract_csv] >> task_transform_cleaning
task_transform_cleaning >> task_transform_enrichment
task_transform_enrichment >> task_transform_dimensions
task_transform_dimensions >> task_transform_facts

# Phase 3: Chargement
task_transform_facts >> task_load_dimensions
task_load_dimensions >> [task_load_fact_consommation, task_load_fact_rentabilite, task_load_fact_environnement]

# Phase 4: Rapport et notification
[task_load_fact_consommation, task_load_fact_rentabilite, task_load_fact_environnement] >> task_generate_report
task_generate_report >> task_email_success

