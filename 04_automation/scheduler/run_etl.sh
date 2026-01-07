#!/bin/bash
################################################################################
# Script d'exécution de l'ETL GreenCity
################################################################################
# Auteur: Équipe BI GreenCity
# Date: Janvier 2026
# Description: Script pour exécuter le processus ETL complet
#              À utiliser avec cron (Linux/MacOS) ou Task Scheduler (Windows)
################################################################################

# Configuration
PROJECT_HOME="/Users/mohammedbelouarraq/Desktop/BI"
PENTAHO_HOME="/opt/pentaho/data-integration"
LOG_DIR="${PROJECT_HOME}/logs"
ETL_JOB="${PROJECT_HOME}/03_etl/pentaho/jobs/main_etl_job.kjb"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/etl_${DATE}.log"

# Créer le répertoire de logs s'il n'existe pas
mkdir -p "${LOG_DIR}"

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Fonction d'envoi d'email (optionnel)
send_email() {
    local subject="$1"
    local message="$2"
    
    # Utiliser mail (si disponible)
    if command -v mail &> /dev/null; then
        echo "${message}" | mail -s "${subject}" admin@greencity.com
    fi
}

# Début de l'exécution
log "========================================="
log "Début de l'exécution de l'ETL GreenCity"
log "========================================="

# Vérifier que Pentaho est installé
if [ ! -d "${PENTAHO_HOME}" ]; then
    log "ERREUR: Pentaho Data Integration introuvable dans ${PENTAHO_HOME}"
    send_email "[GreenCity ETL] ERREUR" "Pentaho Data Integration introuvable"
    exit 1
fi

# Vérifier que le job ETL existe
if [ ! -f "${ETL_JOB}" ]; then
    log "ERREUR: Job ETL introuvable: ${ETL_JOB}"
    send_email "[GreenCity ETL] ERREUR" "Job ETL introuvable"
    exit 1
fi

# Exécuter le job Pentaho
log "Exécution du job ETL: ${ETL_JOB}"
cd "${PENTAHO_HOME}" || exit 1

./kitchen.sh \
    -file="${ETL_JOB}" \
    -level=Basic \
    -param:PROJECT_HOME="${PROJECT_HOME}" \
    -param:EXECUTION_DATE="${DATE}" \
    >> "${LOG_FILE}" 2>&1

# Vérifier le code de retour
EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    log "========================================="
    log "ETL terminé avec SUCCÈS"
    log "========================================="
    send_email "[GreenCity ETL] SUCCÈS" "L'ETL s'est terminé avec succès. Consultez ${LOG_FILE} pour plus de détails."
else
    log "========================================="
    log "ETL terminé avec ERREUR (code: ${EXIT_CODE})"
    log "========================================="
    send_email "[GreenCity ETL] ERREUR" "L'ETL a échoué avec le code ${EXIT_CODE}. Consultez ${LOG_FILE} pour plus de détails."
fi

# Archiver les anciens logs (garder les 30 derniers jours)
log "Nettoyage des anciens logs..."
find "${LOG_DIR}" -name "etl_*.log" -type f -mtime +30 -delete

log "Fin de l'exécution"
exit ${EXIT_CODE}

