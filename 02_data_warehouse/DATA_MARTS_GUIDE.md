# 📊 Guide des Data Marts - GreenCity DW

**Date**: 06 janvier 2026  
**Statut**: Prêt pour implémentation  
**Pipeline ETL**: ✅ 100% Complet (32 transformations)

---

## 🎯 Vue d'Ensemble

Le Data Warehouse GreenCity contient **3 Data Marts** en architecture étoile, chacun dédié à un domaine d'analyse spécifique:

1. 📊 **Data Mart Consommation Énergétique**
2. 💰 **Data Mart Rentabilité Économique**
3. 🌱 **Data Mart Impact Environnemental**

---

## 🗂️ Architecture du Data Warehouse

### Base de Données: `greencity_dw`

```
greencity_dw/
│
├── DIMENSIONS PARTAGÉES (6 tables)
│   ├── dim_date              ← Dimension temporelle
│   ├── dim_region            ← Localisation (SCD Type 2)
│   ├── dim_batiment          ← Bâtiments (SCD Type 2)
│   ├── dim_client            ← Clients (SCD Type 2)
│   ├── dim_compteur          ← Compteurs énergétiques
│   └── dim_type_energie      ← Types d'énergie (eau/élec/gaz)
│
└── TABLES DE FAITS (3 tables)
    ├── fact_consommation     ← Data Mart #1: Consommation
    ├── fact_rentabilite      ← Data Mart #2: Rentabilité
    └── fact_environnement    ← Data Mart #3: Environnement
```

---

## 📊 Data Mart #1: Consommation Énergétique

### Objectif

Analyser et optimiser la consommation énergétique des bâtiments intelligents par type d'énergie, période et localisation.

### Schéma en Étoile

```
                    dim_date
                       │
                       │
    dim_region ─── fact_consommation ─── dim_compteur
                       │
                       │
                 dim_batiment
                       │
                       │
                 dim_type_energie
```

### Table de Faits: `fact_consommation`

**Clés**:

- `id_consommation` (PK)
- `id_date` (FK → dim_date)
- `id_batiment` (FK → dim_batiment)
- `id_compteur` (FK → dim_compteur)
- `id_type_energie` (FK → dim_type_energie)
- `id_region` (FK → dim_region)

**Métriques**:

- `consommation` (DECIMAL) - Quantité consommée
- `unite` (VARCHAR) - m³ ou kWh
- `cout_unitaire` (DECIMAL) - Prix unitaire
- `cout_total` (DECIMAL) - Coût total
- `consommation_moyenne_jour` (DECIMAL) - Moyenne journalière
- `consommation_totale_mois` (DECIMAL) - Total mensuel

**Dimensions**:

- `heure` (INT) - Heure de mesure (0-23)
- `date_mesure` (DATE) - Date de la mesure

### Questions d'Analyse

1. **Consommation par période**

   - Quelle est la consommation totale par mois/trimestre/année?
   - Quelles sont les heures de pointe de consommation?
   - Évolution de la consommation dans le temps?

2. **Consommation par type d'énergie**

   - Répartition eau/électricité/gaz?
   - Quel type d'énergie coûte le plus cher?
   - Optimisation du mix énergétique?

3. **Consommation par localisation**

   - Quelles régions consomment le plus?
   - Impact de la zone climatique?
   - Comparaison entre bâtiments?

4. **Performance énergétique**
   - Identification des bâtiments énergivores
   - Détection des anomalies de consommation
   - Efficacité des compteurs

### KPIs Principaux

- 📊 **Consommation Totale** (par période/région/type)
- 💰 **Coût Énergétique Total**
- 📈 **Tendance de Consommation** (YoY, MoM)
- ⚡ **Heures de Pointe**
- 🏆 **Top/Bottom Bâtiments** (consommation)
- 📉 **Économies Réalisées**

---

## 💰 Data Mart #2: Rentabilité Économique

### Objectif

Analyser la rentabilité économique, le recouvrement des factures, et la performance financière par client et région.

### Schéma en Étoile

```
                    dim_date
                       │
                       │
    dim_region ─── fact_rentabilite ─── dim_client
                       │
                       │
                 dim_batiment
```

### Table de Faits: `fact_rentabilite`

**Clés**:

- `id_rentabilite` (PK)
- `id_date` (FK → dim_date)
- `id_client` (FK → dim_client)
- `id_batiment` (FK → dim_batiment)
- `id_region` (FK → dim_region)

**Métriques Financières**:

- `montant_ht` (DECIMAL) - Montant hors taxes
- `montant_tva` (DECIMAL) - Montant de la TVA
- `montant_ttc` (DECIMAL) - Montant TTC
- `marge` (DECIMAL) - Marge bénéficiaire
- `taux_marge` (DECIMAL) - Taux de marge (%)

**Métriques de Paiement**:

- `date_facture` (DATE)
- `date_echeance` (DATE)
- `date_paiement` (DATE)
- `delai_paiement` (INT) - Jours de délai
- `statut_paiement` (VARCHAR) - Payé/Impayé/En retard
- `montant_impaye` (DECIMAL)

**Métriques Calculées**:

- `roi` (DECIMAL) - Return on Investment
- `taux_recouvrement` (DECIMAL) - % factures payées
- `dso` (INT) - Days Sales Outstanding

### Questions d'Analyse

1. **Performance Financière**

   - Chiffre d'affaires par période?
   - Évolution de la marge?
   - Rentabilité par client/région?

2. **Recouvrement**

   - Taux de paiement à échéance?
   - Montant des impayés?
   - Délai moyen de paiement (DSO)?
   - Clients à risque?

3. **Analyse Client**

   - Top clients par CA?
   - Clients les plus rentables?
   - Segmentation client?

4. **Performance Régionale**
   - Régions les plus rentables?
   - Concentration du CA?
   - Potentiel de croissance?

### KPIs Principaux

- 💵 **Chiffre d'Affaires** (CA)
- 📊 **Marge Bénéficiaire**
- 💯 **Taux de Recouvrement**
- ⏱️ **DSO** (Days Sales Outstanding)
- 🎯 **ROI** par client/région
- 📈 **Croissance CA** (YoY, MoM)
- ⚠️ **Impayés & Retards**

---

## 🌱 Data Mart #3: Impact Environnemental

### Objectif

Mesurer et suivre l'impact environnemental des bâtiments (émissions CO2, recyclage) et la performance écologique.

### Schéma en Étoile

```
                    dim_date
                       │
                       │
    dim_region ─── fact_environnement ─── dim_batiment
```

### Table de Faits: `fact_environnement`

**Clés**:

- `id_environnement` (PK)
- `id_date` (FK → dim_date)
- `id_batiment` (FK → dim_batiment)
- `id_region` (FK → dim_region)

**Métriques Environnementales**:

- `emission_co2_kg` (DECIMAL) - Émissions CO2 en kg
- `taux_recyclage` (DECIMAL) - Taux de recyclage (0-1)
- `dechets_kg` (DECIMAL) - Quantité de déchets
- `dechets_recycles_kg` (DECIMAL) - Déchets recyclés

**Métriques Calculées**:

- `ratio_co2_consommation` (DECIMAL) - kg CO2 / unité énergie
- `emission_co2_moyenne_region` (DECIMAL)
- `performance_environnementale` (VARCHAR) - Excellent/Bon/Moyen/Faible
- `conformite_objectifs` (BOOLEAN)

**Indicateurs**:

- `objectif_co2_kg` (DECIMAL) - Objectif fixé
- `ecart_objectif_co2` (DECIMAL) - Écart à l'objectif
- `taux_atteinte_objectif` (DECIMAL) - %

### Questions d'Analyse

1. **Émissions CO2**

   - Total des émissions par période?
   - Évolution des émissions?
   - Bâtiments les plus polluants?
   - Impact de la consommation énergétique?

2. **Recyclage**

   - Taux de recyclage moyen?
   - Progression du recyclage?
   - Comparaison entre régions?

3. **Performance Environnementale**

   - Atteinte des objectifs CO2?
   - Bâtiments certifiés verts?
   - ROI des investissements écologiques?

4. **Corrélations**
   - Lien consommation/CO2?
   - Impact zone climatique?
   - Efficacité des actions écologiques?

### KPIs Principaux

- 🌍 **Émissions CO2 Totales**
- ♻️ **Taux de Recyclage Moyen**
- 📉 **Réduction CO2** (vs période précédente)
- 🎯 **Atteinte Objectifs Environnementaux**
- 🏆 **Score Environnemental** par bâtiment
- 📊 **Ratio CO2/Consommation**
- 🌱 **Bâtiments Verts** (certification)

---

## 🔄 Dimensions Partagées (Détails)

### dim_date (Dimension Temporelle)

**Attributs**:

- Composantes: jour, mois, année, trimestre, semestre
- Noms: nom_mois, nom_jour_semaine
- Indicateurs: jour_semaine, jour_annee, semaine_annee
- Flags: est_weekend, est_jour_ferie
- Périodes: periode_mois (YYYY-MM), periode_trimestre (YYYY-Q1)
- Saison: printemps/été/automne/hiver

**Pré-remplie** via script: `02_populate_dim_date.sql`

---

### dim_region (Dimension Géographique - SCD Type 2)

**Attributs**:

- `code_region` (REG01, REG02...)
- `nom_region`
- `pays`
- `zone_climatique` (Méditerranéen, Continental...)
- `population`
- `superficie_km2`

**Historisation** (SCD Type 2):

- `date_debut`, `date_fin`, `est_actuel`

---

### dim_batiment (Dimension Bâtiment - SCD Type 2)

**Attributs**:

- `code_batiment` (BAT001, BAT002...)
- `nom_batiment`
- `adresse`, `ville`, `code_postal`
- `type_batiment` (Bureau, Résidentiel, Commercial, Industriel)
- `surface_m2`
- `nb_etages`
- `annee_construction`
- `certification_environnementale` (LEED, HQE, BREEAM)

**Historisation** (SCD Type 2):

- `date_debut`, `date_fin`, `est_actuel`

---

### dim_client (Dimension Client - SCD Type 2)

**Attributs**:

- `code_client` (CLI001, CLI002...)
- `nom_entreprise`
- `secteur_activite`
- `taille_entreprise`
- `email`, `telephone`
- `segment_client` (Particulier, PME, Grande Entreprise)

**Historisation** (SCD Type 2):

- `date_debut`, `date_fin`, `est_actuel`

---

### dim_compteur (Dimension Compteur)

**Attributs**:

- `code_compteur` (EAU_0101, ELEC_0101, GAZ_0101)
- `type_compteur` (Eau, Électricité, Gaz)
- `modele_compteur`
- `date_installation`
- `date_derniere_maintenance`
- `statut_compteur` (Actif, En maintenance, Hors service)

---

### dim_type_energie (Dimension Référence)

**Attributs**:

- `code_type_energie` (EAU, ELEC, GAZ)
- `nom_type_energie` (Eau, Électricité, Gaz)
- `unite_mesure` (m³, kWh)
- `facteur_emission_co2` (kg CO2/unité)
- `cout_moyen_unitaire`
- `renouvelable` (BOOLEAN)

---

## 🚀 Ordre d'Implémentation

### Phase 1: Création de la Base de Données ✅

```sql
-- Exécuter:
source 02_data_warehouse/schema/01_create_datawarehouse.sql

-- Vérifie:
USE greencity_dw;
SHOW TABLES;  -- Doit afficher 9 tables
```

### Phase 2: Population dim_date ✅

```sql
-- Exécuter:
source 02_data_warehouse/schema/02_populate_dim_date.sql

-- Vérifie:
SELECT COUNT(*) FROM dim_date;  -- Doit retourner 365+ lignes
```

### Phase 3: Exécution Pipeline ETL Pentaho

**Ordre d'exécution** (via Pentaho Spoon ou Kitchen):

```bash
# 1. EXTRACTION (8 transformations)
cd 03_etl/pentaho/transformations/extractions/
kitchen.sh -file=01_extraction_mysql.ktr
kitchen.sh -file=02_extraction_mysql_buildings.ktr
# ... tous les autres

# 2. NETTOYAGE (8 transformations)
cd ../nettoyage/
kitchen.sh -file=04_transformation_nettoyage_clients.ktr
# ... tous les autres

# 3. ENRICHISSEMENT (6 transformations)
cd ../enrichissement/
kitchen.sh -file=05_transformation_enrichissement_factures.ktr
# ... tous les autres

# 4. DIMENSIONS (5 transformations)
cd ../dimensions/
kitchen.sh -file=06a_preparation_dim_client.ktr
# ... tous les autres

# 5. FAITS (3 transformations)
cd ../faits/
kitchen.sh -file=07a_preparation_fact_consommation.ktr
# ... tous les autres

# 6. CHARGEMENT (2 transformations)
cd ../chargement/
kitchen.sh -file=08a_chargement_dimensions.ktr
kitchen.sh -file=08b_chargement_faits.ktr
```

### Phase 4: Validation des Données

```sql
-- Vérifier le chargement des dimensions
SELECT 'dim_date' AS table_name, COUNT(*) AS rows FROM dim_date
UNION ALL
SELECT 'dim_region', COUNT(*) FROM dim_region
UNION ALL
SELECT 'dim_batiment', COUNT(*) FROM dim_batiment
UNION ALL
SELECT 'dim_client', COUNT(*) FROM dim_client
UNION ALL
SELECT 'dim_compteur', COUNT(*) FROM dim_compteur
UNION ALL
SELECT 'dim_type_energie', COUNT(*) FROM dim_type_energie;

-- Vérifier le chargement des faits
SELECT 'fact_consommation' AS table_name, COUNT(*) AS rows FROM fact_consommation
UNION ALL
SELECT 'fact_rentabilite', COUNT(*) FROM fact_rentabilite
UNION ALL
SELECT 'fact_environnement', COUNT(*) FROM fact_environnement;

-- Vérifier l'intégrité référentielle
SELECT
    f.id_consommation,
    d.date,
    b.nom_batiment,
    te.nom_type_energie,
    f.consommation
FROM fact_consommation f
JOIN dim_date d ON f.id_date = d.id_date
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
JOIN dim_type_energie te ON f.id_type_energie = te.id_type_energie
LIMIT 10;
```

### Phase 5: Configuration Power BI

1. **Connexion à la base**:

   - Connecter Power BI à MySQL
   - Base: `greencity_dw`

2. **Import des tables**:

   - Importer les 6 dimensions
   - Importer les 3 tables de faits

3. **Création des relations**:

   - Configurer les relations FK → PK
   - Vérifier la cardinalité (1:N)

4. **Création des dashboards**:
   - Dashboard Consommation
   - Dashboard Rentabilité
   - Dashboard Environnement

---

## 📊 Exemples de Requêtes Analytiques

### Data Mart Consommation

```sql
-- Consommation totale par type d'énergie et par mois
SELECT
    d.periode_mois,
    te.nom_type_energie,
    SUM(f.consommation) AS consommation_totale,
    AVG(f.cout_unitaire) AS cout_moyen,
    SUM(f.cout_total) AS cout_total
FROM fact_consommation f
JOIN dim_date d ON f.id_date = d.id_date
JOIN dim_type_energie te ON f.id_type_energie = te.id_type_energie
WHERE d.annee = 2024
GROUP BY d.periode_mois, te.nom_type_energie
ORDER BY d.periode_mois, te.nom_type_energie;
```

### Data Mart Rentabilité

```sql
-- Top 10 clients par chiffre d'affaires
SELECT
    c.nom_entreprise,
    c.secteur_activite,
    COUNT(f.id_rentabilite) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    AVG(f.taux_marge) AS marge_moyenne,
    AVG(f.delai_paiement) AS delai_moyen
FROM fact_rentabilite f
JOIN dim_client c ON f.id_client = c.id_client
WHERE c.est_actuel = TRUE
GROUP BY c.id_client
ORDER BY ca_total DESC
LIMIT 10;
```

### Data Mart Environnement

```sql
-- Performance environnementale par région
SELECT
    r.nom_region,
    r.zone_climatique,
    COUNT(DISTINCT f.id_batiment) AS nb_batiments,
    SUM(f.emission_co2_kg) AS emissions_totales,
    AVG(f.taux_recyclage) * 100 AS taux_recyclage_moyen,
    AVG(f.ratio_co2_consommation) AS ratio_moyen
FROM fact_environnement f
JOIN dim_region r ON f.id_region = r.id_region
JOIN dim_date d ON f.id_date = d.id_date
WHERE d.annee = 2024 AND r.est_actuel = TRUE
GROUP BY r.id_region
ORDER BY emissions_totales DESC;
```

---

## ✅ Checklist d'Implémentation

### Préparation ✅

- [x] Pipeline ETL complet (32 transformations)
- [x] Schéma Data Warehouse défini
- [x] Scripts SQL de création
- [x] Documentation complète

### Création Base ⏳

- [ ] Exécuter 01_create_datawarehouse.sql
- [ ] Exécuter 02_populate_dim_date.sql
- [ ] Vérifier les tables créées

### Chargement Données ⏳

- [ ] Exécuter pipeline extraction
- [ ] Exécuter pipeline nettoyage
- [ ] Exécuter pipeline enrichissement
- [ ] Exécuter pipeline dimensions
- [ ] Exécuter pipeline faits
- [ ] Exécuter pipeline chargement

### Validation ⏳

- [ ] Vérifier nombre de lignes par table
- [ ] Tester intégrité référentielle
- [ ] Valider agrégations
- [ ] Tester requêtes analytiques

### Reporting ⏳

- [ ] Connecter Power BI
- [ ] Créer modèle de données
- [ ] Développer dashboards
- [ ] Publier rapports

---

## 📞 Contacts & Références

**Documents**:

- `/02_data_warehouse/design/DATA_MARTS_DESIGN.md`
- `/03_etl/pentaho/PIPELINE_COMPLETE.md`
- `/05_reporting/README_REPORTING.md`

**Scripts SQL**:

- `/02_data_warehouse/schema/01_create_datawarehouse.sql`
- `/02_data_warehouse/schema/02_populate_dim_date.sql`

**Transformations Pentaho**:

- `/03_etl/pentaho/transformations/` (32 fichiers .ktr)

---

_Guide créé le: 06 janvier 2026_  
_Projet: BI Consommation Énergétique 2024_  
_Équipe: Génie Informatique 2025-2026_
