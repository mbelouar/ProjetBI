"""
Script d'Orchestration Principal ETL - GreenCity BI
Orchestre toutes les étapes: Extraction -> Transformation -> Chargement
"""
import sys
import os
import subprocess
from datetime import datetime
import traceback

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration des chemins
BASE_DIR = r"D:\BI"
SCRIPTS_DIR = os.path.join(BASE_DIR, "03_etl", "scripts")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

def ensure_logs_dir():
    """Créer le dossier logs s'il n'existe pas"""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def log_message(message, level="INFO"):
    """Afficher et logger un message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    log_file = os.path.join(LOGS_DIR, f"etl_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def run_script(script_name, description):
    """Exécuter un script Python et gérer les erreurs"""
    log_message(f"▶ Démarrage: {description} ({script_name})")
    
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    
    if not os.path.exists(script_path):
        log_message(f"❌ Script introuvable: {script_path}", "ERROR")
        return False
    
    try:
        # Exécuter le script
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=SCRIPTS_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            log_message(f"✅ Terminé: {description}", "SUCCESS")
            if result.stdout:
                # Afficher les dernières lignes de la sortie
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:  # Dernières 5 lignes
                    if line.strip():
                        log_message(f"   {line}", "INFO")
            return True
        else:
            log_message(f"❌ Échec: {description}", "ERROR")
            if result.stderr:
                log_message(f"   Erreur: {result.stderr[:500]}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"❌ Exception lors de l'exécution de {script_name}: {str(e)}", "ERROR")
        log_message(f"   {traceback.format_exc()}", "ERROR")
        return False

def check_prerequisites():
    """Vérifier les prérequis"""
    log_message("🔍 Vérification des prérequis...")
    
    checks_passed = True
    
    # Vérifier la configuration
    config_file = os.path.join(BASE_DIR, "config", "database_config.ini")
    if not os.path.exists(config_file):
        log_message(f"❌ Fichier de configuration introuvable: {config_file}", "ERROR")
        checks_passed = False
    
    # Vérifier les répertoires
    dirs_to_check = [
        os.path.join(BASE_DIR, "01_operational_sources", "json"),
        os.path.join(BASE_DIR, "01_operational_sources", "csv"),
        os.path.join(BASE_DIR, "03_etl", "staging", "extracted"),
        os.path.join(BASE_DIR, "03_etl", "staging", "transformed"),
    ]
    
    for dir_path in dirs_to_check:
        if not os.path.exists(dir_path):
            log_message(f"⚠ Répertoire manquant (création): {dir_path}", "WARNING")
            os.makedirs(dir_path, exist_ok=True)
    
    if checks_passed:
        log_message("✅ Tous les prérequis sont OK", "SUCCESS")
    
    return checks_passed

def main():
    """Fonction principale d'orchestration"""
    print("=" * 70)
    print("ETL ORCHESTRATOR - GreenCity BI")
    print("=" * 70)
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    ensure_logs_dir()
    log_message("🚀 Démarrage du processus ETL complet")
    
    # Vérification des prérequis
    if not check_prerequisites():
        log_message("❌ Échec des vérifications préalables. Arrêt du processus.", "ERROR")
        return 1
    
    steps_failed = []
    steps_succeeded = []
    
    # ========================================================================
    # PHASE 1: EXTRACTION (E)
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 1: EXTRACTION")
    log_message("=" * 70)
    
    extraction_steps = [
        ("extract_regions_mysql.py", "Extraction régions (MySQL)"),
        ("convert_json_elec_to_csv.py", "Extraction consommation électricité (JSON)"),
        ("convert_json_gaz_to_csv.py", "Extraction consommation gaz (JSON)"),
        ("convert_csv_environnement_to_extracted.py", "Extraction données environnementales (CSV)"),
    ]
    
    for script, description in extraction_steps:
        success = run_script(script, description)
        if success:
            steps_succeeded.append(description)
        else:
            steps_failed.append(description)
            log_message(f"⚠ Continuation malgré l'échec de: {description}", "WARNING")
    
    # ========================================================================
    # PHASE 2: TRANSFORMATION - NETTOYAGE & ENRICHISSEMENT
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 2: TRANSFORMATION (Nettoyage & Enrichissement)")
    log_message("=" * 70)
    
    # Note: Les scripts de nettoyage/enrichissement peuvent être exécutés ici
    # Pour l'instant, on passe directement aux transformations de dimensions
    
    # ========================================================================
    # PHASE 3: TRANSFORMATION - DIMENSIONS
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 3: TRANSFORMATION - PRÉPARATION DES DIMENSIONS")
    log_message("=" * 70)
    
    if run_script("06_transformation_dimensions.py", "Transformation des dimensions"):
        steps_succeeded.append("Transformation dimensions")
    else:
        steps_failed.append("Transformation dimensions")
        log_message("❌ Échec critique: Transformation des dimensions. Arrêt.", "ERROR")
        return 1
    
    # ========================================================================
    # PHASE 4: TRANSFORMATION - FAITS
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 4: TRANSFORMATION - PRÉPARATION DES FAITS")
    log_message("=" * 70)
    
    if run_script("07_transformation_faits.py", "Transformation des tables de faits"):
        steps_succeeded.append("Transformation faits")
    else:
        steps_failed.append("Transformation faits")
        log_message("❌ Échec critique: Transformation des faits. Arrêt.", "ERROR")
        return 1
    
    # ========================================================================
    # PHASE 5: CHARGEMENT - DIMENSIONS
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 5: CHARGEMENT - DIMENSIONS")
    log_message("=" * 70)
    
    if run_script("08_chargement_dimensions.py", "Chargement des dimensions dans le DW"):
        steps_succeeded.append("Chargement dimensions")
    else:
        steps_failed.append("Chargement dimensions")
        log_message("❌ Échec critique: Chargement des dimensions. Arrêt.", "ERROR")
        return 1
    
    # ========================================================================
    # PHASE 6: CHARGEMENT - FAITS
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("PHASE 6: CHARGEMENT - TABLES DE FAITS")
    log_message("=" * 70)
    
    loading_steps = [
        ("09_chargement_fait_consommation.py", "Chargement fact_consommation"),
        ("10_chargement_fait_rentabilite.py", "Chargement fact_rentabilite"),
        ("11_chargement_fait_environnement.py", "Chargement fact_environnement"),
    ]
    
    for script, description in loading_steps:
        success = run_script(script, description)
        if success:
            steps_succeeded.append(description)
        else:
            steps_failed.append(description)
            log_message(f"⚠ Continuation malgré l'échec de: {description}", "WARNING")
    
    # ========================================================================
    # RÉSUMÉ FINAL
    # ========================================================================
    log_message("\n" + "=" * 70)
    log_message("RÉSUMÉ DE L'EXÉCUTION")
    log_message("=" * 70)
    
    log_message(f"✅ Étapes réussies: {len(steps_succeeded)}")
    for step in steps_succeeded:
        log_message(f"   ✓ {step}", "SUCCESS")
    
    if steps_failed:
        log_message(f"\n❌ Étapes échouées: {len(steps_failed)}")
        for step in steps_failed:
            log_message(f"   ✗ {step}", "ERROR")
    else:
        log_message("\n🎉 Toutes les étapes ont réussi !", "SUCCESS")
    
    log_message(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 70)
    
    return 0 if not steps_failed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

