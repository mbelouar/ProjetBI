# 📋 Guide des Jobs Pentaho - Automatisation ETL

**Date**: 06 janvier 2026  
**Statut**: ✅ Job principal créé

---

## 🎯 Vue d'Ensemble

Les jobs Pentaho (`.kjb`) permettent d'automatiser l'exécution de plusieurs transformations dans un ordre défini, avec gestion des erreurs et logging.

---

## 📁 Jobs Disponibles

### ✅ 01_main_etl_job.kjb

**Description**: Job principal qui orchestre l'exécution complète du pipeline ETL (32 transformations)

**Structure**:
```
START
  │
  ├─► Check_DB_Connections (Vérifier connexions MySQL)
  │
  ├─► PHASE 1: EXTRACTION (8 transformations en parallèle)
  │     ├─► Extract_MySQL_Regions
  │     ├─► Extract_MySQL_Buildings
  │     ├─► Extract_MySQL_Clients
  │     ├─► Extract_MySQL_Compteurs
  │     ├─► Extract_MySQL_Factures
  │     ├─► Extract_JSON_Eau
  │     ├─► Extract_JSON_Elec
  │     └─► Extract_JSON_Gaz
  │     └─► Wait_Extraction_Complete
  │
  ├─► PHASE 2: NETTOYAGE (8 transformations en parallèle)
  │     ├─► Clean_Clients
  │     ├─► Clean_Batiments
  │     ├─► Clean_Factures
  │     ├─► Clean_Regions
  │     ├─► Clean_Consommation_Eau
  │     ├─► Clean_Consommation_Elec
  │     ├─► Clean_Consommation_Gaz
  │     └─► Clean_Environnement
  │     └─► Wait_Cleaning_Complete
  │
  ├─► PHASE 3: ENRICHISSEMENT (6 transformations en parallèle)
  │     ├─► Enrich_Factures
  │     ├─► Enrich_Consommation_Eau
  │     ├─► Enrich_Consommation_Elec
  │     ├─► Enrich_Consommation_Gaz
  │     ├─► Enrich_Environnement
  │     └─► Enrich_Regions
  │     └─► Wait_Enrichment_Complete
  │
  ├─► PHASE 4: DIMENSIONS (5 transformations en parallèle)
  │     ├─► Prepare_Dim_Client
  │     ├─► Prepare_Dim_Batiment
  │     ├─► Prepare_Dim_Compteur
  │     ├─► Prepare_Dim_Region
  │     └─► Prepare_Dim_Type_Energie
  │     └─► Wait_Dimensions_Complete
  │
  ├─► PHASE 5: FAITS (3 transformations en parallèle)
  │     ├─► Prepare_Fact_Consommation
  │     ├─► Prepare_Fact_Rentabilite
  │     └─► Prepare_Fact_Environnement
  │     └─► Wait_Facts_Complete
  │
  ├─► PHASE 6: CHARGEMENT (séquentiel)
  │     ├─► Load_Dimensions (SCD Type 2)
  │     └─► Load_Facts (incrémental)
  │
  ├─► Success_Message
  │
  └─► END
```

**Total**: 32 transformations orchestrées automatiquement

---

## 🚀 Exécution du Job

### Option 1: Via Pentaho Spoon (GUI)

1. Ouvrir Pentaho Spoon
2. **File** → **Open** → Sélectionner `01_main_etl_job.kjb`
3. Cliquer sur **Run** (▶️)
4. Observer l'exécution dans la console

### Option 2: Via Kitchen (Ligne de commande)

```bash
# Linux/Mac
cd /opt/pentaho/data-integration
./kitchen.sh -file="/Users/mohammedbelouarraq/Desktop/BI 2/03_etl/pentaho/jobs/01_main_etl_job.kjb" -level=Basic

# Windows
cd C:\pentaho\data-integration
kitchen.bat -file="C:\Users\...\BI 2\03_etl\pentaho\jobs\01_main_etl_job.kjb" -level=Basic
```

### Option 3: Via Script Shell (Automatisation)

```bash
# Script shell pour exécution automatique
#!/bin/bash
cd /opt/pentaho/data-integration
./kitchen.sh -file="/path/to/01_main_etl_job.kjb" \
  -level=Basic \
  -logfile=/path/to/logs/etl_$(date +%Y%m%d_%H%M%S).log
```

---

## 📊 Flux d'Exécution

### Phase 1: Extraction (Parallèle)
- **8 transformations** exécutées en parallèle
- **Temps estimé**: 5-10 minutes
- **Sortie**: 9 fichiers CSV dans `staging/extracted/`

### Phase 2: Nettoyage (Parallèle)
- **8 transformations** exécutées en parallèle
- **Temps estimé**: 10-15 minutes
- **Sortie**: 8 fichiers CSV dans `staging/transformed/*_cleaned.csv`

### Phase 3: Enrichissement (Parallèle)
- **6 transformations** exécutées en parallèle
- **Temps estimé**: 15-20 minutes
- **Sortie**: 6 fichiers CSV dans `staging/transformed/*_enriched.csv`

### Phase 4: Dimensions (Parallèle)
- **5 transformations** exécutées en parallèle
- **Temps estimé**: 10-15 minutes
- **Sortie**: 5 fichiers CSV dans `staging/transformed/dim_*_ready.csv`

### Phase 5: Faits (Parallèle)
- **3 transformations** exécutées en parallèle
- **Temps estimé**: 10-15 minutes
- **Sortie**: 3 fichiers CSV dans `staging/transformed/fact_*_ready.csv`

### Phase 6: Chargement (Séquentiel)
- **2 transformations** exécutées séquentiellement
- **Temps estimé**: 5-10 minutes
- **Sortie**: Données chargées dans `greencity_dw`

**Temps total estimé**: 55-85 minutes

---

## 🔍 Gestion des Erreurs

### Comportement par défaut
- Si une transformation échoue, le job s'arrête
- Les erreurs sont loggées dans la console et les fichiers de log

### Options de gestion d'erreurs (à configurer dans Spoon)
1. **Clic droit sur un hop** → **Evaluation**
2. Sélectionner **Follow when result is false** (en cas d'erreur)
3. Connecter vers une étape de gestion d'erreur (ex: Send Email, Write to Log)

### Exemple: Ajouter gestion d'erreur
```
Transformation (succès) ──► Next Step
Transformation (erreur) ──► Error_Handler ──► Send_Email ──► END
```

---

## 📝 Logging

### Niveaux de log disponibles
- **Minimal**: Erreurs uniquement
- **Basic**: Erreurs + informations de base
- **Detailed**: Informations détaillées
- **Debug**: Toutes les informations de débogage
- **Rowlevel**: Informations ligne par ligne (très verbeux)

### Fichiers de log
Par défaut, les logs sont affichés dans la console. Pour sauvegarder dans un fichier:

```bash
kitchen.sh -file="job.kjb" \
  -level=Basic \
  -logfile=/path/to/logs/etl_$(date +%Y%m%d_%H%M%S).log
```

---

## ⏰ Planification (Scheduling)

### Option 1: Cron (Linux/Mac)

```bash
# Éditer crontab
crontab -e

# Exécuter le job tous les jours à 2h du matin
0 2 * * * /opt/pentaho/data-integration/kitchen.sh -file="/path/to/01_main_etl_job.kjb" -level=Basic >> /var/log/etl.log 2>&1
```

### Option 2: Task Scheduler (Windows)

1. Ouvrir **Planificateur de tâches**
2. Créer une tâche de base
3. Action: Démarrer un programme
4. Programme: `C:\pentaho\data-integration\kitchen.bat`
5. Arguments: `-file="C:\path\to\01_main_etl_job.kjb" -level=Basic`
6. Planifier: Quotidien à 2h00

### Option 3: Apache Airflow

Créer un DAG Airflow qui appelle le job Pentaho:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG('etl_pipeline', schedule_interval='0 2 * * *')

run_etl = BashOperator(
    task_id='run_pentaho_job',
    bash_command='/opt/pentaho/data-integration/kitchen.sh -file="/path/to/01_main_etl_job.kjb"',
    dag=dag
)
```

---

## ✅ Checklist d'Exécution

### Avant l'exécution
- [ ] Vérifier que MySQL est démarré
- [ ] Vérifier les connexions dans Spoon (View → Database connections)
- [ ] Vérifier que les fichiers sources existent
- [ ] Vérifier les permissions d'écriture dans `staging/`

### Pendant l'exécution
- [ ] Surveiller les logs pour détecter les erreurs
- [ ] Vérifier l'utilisation CPU/Mémoire
- [ ] Vérifier l'espace disque disponible

### Après l'exécution
- [ ] Vérifier que tous les fichiers CSV ont été générés
- [ ] Vérifier les logs pour confirmer le succès
- [ ] Valider les données dans le Data Warehouse
- [ ] Vérifier l'intégrité référentielle

---

## 🔧 Configuration Avancée

### Variables d'environnement
Le job utilise des variables Pentaho pour les chemins:
- `${Internal.Job.Filename.Directory}` - Répertoire du job
- Les transformations utilisent des chemins relatifs basés sur cette variable

### Paramètres du job
Pour rendre le job paramétrable, ajouter des paramètres dans Spoon:
1. **Job** → **Job settings** → **Parameters**
2. Ajouter des paramètres (ex: `DATE_DEBUT`, `DATE_FIN`)
3. Utiliser dans les transformations: `${DATE_DEBUT}`

### Performance
Pour améliorer les performances:
- Augmenter la mémoire allouée à Pentaho
- Exécuter les transformations en parallèle (déjà configuré)
- Optimiser les transformations individuelles

---

## 📊 Monitoring

### Métriques à surveiller
- **Durée d'exécution totale**
- **Nombre de lignes traitées par phase**
- **Taux d'erreur**
- **Utilisation des ressources (CPU, RAM, Disque)**

### Dashboard de monitoring (optionnel)
Créer un dashboard Power BI pour visualiser:
- Historique des exécutions
- Durée par phase
- Nombre de lignes chargées
- Taux de succès/échec

---

## 🐛 Dépannage

### Problème: Job s'arrête à une transformation
**Solution**:
1. Vérifier les logs pour identifier l'erreur
2. Exécuter la transformation individuellement dans Spoon
3. Vérifier les connexions à la base de données
4. Vérifier les permissions sur les fichiers

### Problème: Erreur de connexion MySQL
**Solution**:
1. Vérifier que MySQL est démarré: `sudo systemctl status mysql`
2. Vérifier les credentials dans Spoon
3. Tester la connexion: **View** → **Database connections** → **Test**

### Problème: Fichiers CSV non trouvés
**Solution**:
1. Vérifier les chemins relatifs dans les transformations
2. Vérifier que les fichiers sources existent
3. Vérifier les permissions de lecture

---

## 📚 Références

- **Documentation Pentaho**: https://help.pentaho.com/
- **Guide complet**: `/03_etl/PENTAHO_COMPLETE_GUIDE.md`
- **Transformations**: `/03_etl/pentaho/transformations/README_TRANSFORMATIONS.md`

---

_Document créé le: 06 janvier 2026_  
_Projet: BI Consommation Énergétique 2024_  
_Équipe: Génie Informatique 2025-2026_

