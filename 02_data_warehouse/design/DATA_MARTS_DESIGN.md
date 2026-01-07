# Conception des Data Marts - GreenCity

## Vue d'ensemble

Le Data Warehouse GreenCity est composé de trois Data Marts indépendants, chacun suivant une architecture dimensionnelle en étoile (star schema).

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE GREENCITY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │   Data Mart 1      │  │   Data Mart 2      │                │
│  │   CONSOMMATION     │  │   RENTABILITÉ      │                │
│  │   ÉNERGÉTIQUE      │  │   ÉCONOMIQUE       │                │
│  └────────────────────┘  └────────────────────┘                │
│                                                                  │
│            ┌────────────────────┐                               │
│            │   Data Mart 3      │                               │
│            │   IMPACT           │                               │
│            │   ENVIRONNEMENTAL  │                               │
│            └────────────────────┘                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DIMENSIONS PARTAGÉES (Conformed Dimensions)       │  │
│  │  - dim_date                                               │  │
│  │  - dim_region                                             │  │
│  │  - dim_batiment                                           │  │
│  │  - dim_client                                             │  │
│  │  - dim_type_energie                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Mart 1: Consommation Énergétique

### Objectif
Mesurer, suivre et comparer la quantité d'énergie consommée par client, bâtiment, région et période.

### Schéma en Étoile

```
                    dim_date
                       │
                       │
        dim_region ────┼──── dim_type_energie
                       │
                       │
                  ┌────┴────┐
                  │  FACT   │
                  │  CONSO  │
                  └────┬────┘
                       │
                       │
        dim_client ────┼──── dim_batiment
                       │
                       │
                  dim_compteur
```

### Table de Faits: fact_consommation

**Grain**: Une mesure de consommation par compteur par heure

**Clés étrangères**:
- id_date (lien vers dim_date)
- id_heure (0-23)
- id_batiment (lien vers dim_batiment)
- id_compteur (lien vers dim_compteur)
- id_region (lien vers dim_region)
- id_client (lien vers dim_client)
- id_type_energie (lien vers dim_type_energie)

**Mesures**:
- consommation_kwh: Consommation en kWh (électricité)
- consommation_m3: Consommation en m3 (eau, gaz)
- consommation_normalisee: Consommation convertie en kWh équivalent
- cout_unitaire: Prix unitaire de l'énergie
- cout_total: Coût total de la consommation
- temperature_celsius: Température ambiante
- humidite_pourcent: Taux d'humidité
- consommation_par_m2: Consommation normalisée par surface

**Mesures agrégées possibles**:
- SUM(consommation_normalisee): Consommation totale
- AVG(consommation_normalisee): Consommation moyenne
- MAX(consommation_normalisee): Consommation pic
- COUNT(*): Nombre de mesures

### Dimensions

#### dim_date (Partagée)
- Granularité: Jour
- Attributs: année, mois, trimestre, semaine, jour_semaine, est_weekend, est_jour_ferie
- Hiérarchie: Année → Trimestre → Mois → Semaine → Jour

#### dim_batiment (Partagée)
- Attributs: nom, type, surface_m2, ville, certification_energetique
- Hiérarchie: Région → Ville → Bâtiment
- SCD Type 2 (historique des changements)

#### dim_region (Partagée)
- Attributs: nom_region, pays, zone_climatique, population
- SCD Type 2

#### dim_client (Partagée)
- Attributs: nom, type_client, segment_client, ville
- SCD Type 2

#### dim_compteur
- Attributs: code_compteur, numero_serie, marque, modele, date_installation
- SCD Type 2

#### dim_type_energie (Partagée)
- Attributs: nom_energie, unite_mesure, facteur_emission_co2, categorie
- SCD Type 1 (pas d'historique)

### Requêtes analytiques typiques

```sql
-- 1. Consommation totale par région et mois
SELECT 
    r.nom_region,
    d.annee,
    d.mois,
    SUM(f.consommation_normalisee) AS consommation_totale
FROM fact_consommation f
JOIN dim_region r ON f.id_region = r.id_region
JOIN dim_date d ON f.id_date = d.id_date
WHERE d.annee = 2024
GROUP BY r.nom_region, d.annee, d.mois;

-- 2. Top 10 bâtiments consommateurs
SELECT 
    b.nom_batiment,
    SUM(f.consommation_normalisee) AS consommation_totale
FROM fact_consommation f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
GROUP BY b.nom_batiment
ORDER BY consommation_totale DESC
LIMIT 10;

-- 3. Corrélation consommation-température
SELECT 
    f.temperature_celsius,
    AVG(f.consommation_normalisee) AS consommation_moyenne
FROM fact_consommation f
WHERE f.temperature_celsius IS NOT NULL
GROUP BY f.temperature_celsius;
```

---

## Data Mart 2: Rentabilité Économique

### Objectif
Analyser la performance financière liée aux bâtiments, clients et régions.

### Schéma en Étoile

```
        dim_date_facture
               │
               │
    dim_date_echeance ──┼── dim_date_paiement
               │
               │
          ┌────┴────┐
          │  FACT   │
          │  RENTA  │
          └────┬────┘
               │
               │
    dim_client ┼──── dim_batiment
               │
               │
    dim_region ┴──── dim_type_energie
```

### Table de Faits: fact_rentabilite

**Grain**: Une facture (avec son paiement éventuel)

**Clés étrangères**:
- id_date_facture (lien vers dim_date)
- id_date_echeance (lien vers dim_date)
- id_date_paiement (lien vers dim_date, NULL si pas payé)
- id_batiment (lien vers dim_batiment)
- id_client (lien vers dim_client)
- id_region (lien vers dim_region)
- id_type_energie (lien vers dim_type_energie)

**Identifiants métier**:
- code_facture: Numéro de facture
- code_paiement: Numéro de paiement (NULL si pas payé)

**Mesures de facturation**:
- consommation_quantite: Quantité consommée
- prix_unitaire: Prix unitaire
- montant_ht: Montant hors taxes
- montant_tva: Montant de la TVA
- montant_ttc: Montant toutes taxes comprises

**Mesures de coût**:
- cout_energie: Coût d'achat de l'énergie

**Mesures de rentabilité**:
- marge: montant_ttc - cout_energie
- taux_marge: marge / montant_ttc

**Mesures de paiement**:
- montant_paye: Montant effectivement payé
- montant_restant: montant_ttc - montant_paye
- delai_paiement_jours: Nombre de jours entre facture et paiement
- retard_paiement_jours: Nombre de jours de retard

**Indicateurs booléens**:
- est_paye: TRUE si facture payée
- est_en_retard: TRUE si paiement en retard
- mode_paiement: Virement, Carte, Chèque, etc.

### Requêtes analytiques typiques

```sql
-- 1. Chiffre d'affaires par région
SELECT 
    r.nom_region,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale,
    AVG(f.taux_marge) * 100 AS taux_marge_moyen
FROM fact_rentabilite f
JOIN dim_region r ON f.id_region = r.id_region
GROUP BY r.nom_region;

-- 2. Taux de recouvrement
SELECT 
    COUNT(*) AS nb_factures,
    SUM(CASE WHEN est_paye THEN 1 ELSE 0 END) AS nb_payees,
    SUM(CASE WHEN est_paye THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS taux_recouvrement
FROM fact_rentabilite;

-- 3. Top 10 clients rentables
SELECT 
    c.nom,
    COUNT(*) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale
FROM fact_rentabilite f
JOIN dim_client c ON f.id_client = c.id_client
GROUP BY c.nom
ORDER BY marge_totale DESC
LIMIT 10;
```

---

## Data Mart 3: Impact Environnemental

### Objectif
Évaluer l'empreinte écologique des bâtiments à partir des émissions de CO₂ et du taux de recyclage.

### Schéma en Étoile

```
                 dim_date
                    │
                    │
        dim_region ─┼─── dim_batiment
                    │
                    │
               ┌────┴────┐
               │  FACT   │
               │  ENV    │
               └─────────┘
```

### Table de Faits: fact_environnement

**Grain**: Un rapport mensuel par bâtiment

**Clés étrangères**:
- id_date (lien vers dim_date, date de fin de mois)
- id_batiment (lien vers dim_batiment)
- id_region (lien vers dim_region)

**Mesures environnementales**:
- emission_co2_kg: Émissions de CO₂ en kg
- taux_recyclage: Taux de recyclage (0-1)

**Mesures de consommation agrégées**:
- consommation_totale_kwh: Consommation totale du mois
- consommation_electricite_kwh: Consommation électricité
- consommation_eau_m3: Consommation eau
- consommation_gaz_m3: Consommation gaz

**Mesures calculées**:
- ratio_co2_consommation: kg CO₂ / kWh
- emission_co2_par_m2: kg CO₂ / m2

**Mesures comparatives**:
- emission_co2_mois_precedent: Émissions du mois précédent
- variation_emission_pourcent: Variation en %
- taux_recyclage_mois_precedent: Taux du mois précédent
- variation_recyclage_pourcent: Variation en %

**Indicateurs**:
- est_conforme_norme: Conforme aux normes environnementales
- niveau_performance: Excellent, Bon, Moyen, Faible

### Requêtes analytiques typiques

```sql
-- 1. Émissions totales par région
SELECT 
    r.nom_region,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.taux_recyclage) * 100 AS taux_recyclage_moyen
FROM fact_environnement f
JOIN dim_region r ON f.id_region = r.id_region
GROUP BY r.nom_region;

-- 2. Évolution des émissions
SELECT 
    d.annee,
    d.mois,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.variation_emission_pourcent) AS variation_moyenne
FROM fact_environnement f
JOIN dim_date d ON f.id_date = d.id_date
GROUP BY d.annee, d.mois
ORDER BY d.annee, d.mois;

-- 3. Top 10 bâtiments polluants
SELECT 
    b.nom_batiment,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.ratio_co2_consommation) AS ratio_moyen
FROM fact_environnement f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
GROUP BY b.nom_batiment
ORDER BY emission_totale DESC
LIMIT 10;
```

---

## Dimensions Partagées (Conformed Dimensions)

### Avantages des dimensions conformes

1. **Cohérence**: Même définition dans tous les Data Marts
2. **Intégration**: Possibilité de croiser les analyses
3. **Maintenance**: Mise à jour centralisée
4. **Drill-across**: Navigation entre Data Marts

### dim_date

**Rôle**: Dimension temporelle universelle

**Attributs**:
- id_date (PK): Format YYYYMMDD
- date: Date complète
- jour, mois, annee, trimestre, semestre
- nom_mois, nom_jour_semaine
- jour_semaine (1=Lundi, 7=Dimanche)
- jour_annee, semaine_annee
- est_weekend, est_jour_ferie, nom_jour_ferie
- periode_mois (YYYY-MM)
- periode_trimestre (YYYY-Q1)
- periode_annee (YYYY)
- saison (Hiver, Printemps, Été, Automne)

**Hiérarchies**:
- Année → Semestre → Trimestre → Mois → Semaine → Jour
- Année → Mois → Jour
- Année → Semaine → Jour

**Population**: 2020-2030 (11 ans, ~4000 enregistrements)

### dim_region

**Rôle**: Localisation géographique

**Attributs**:
- id_region (PK, surrogate key)
- code_region (Business key)
- nom_region
- pays
- zone_climatique
- population
- superficie_km2
- date_debut, date_fin, est_actuel (SCD Type 2)

**SCD Type 2**: Historique des changements de population, zone climatique

### dim_batiment

**Rôle**: Bâtiments intelligents

**Attributs**:
- id_batiment (PK, surrogate key)
- code_batiment (Business key)
- nom_batiment
- id_region (FK)
- type_batiment (Bureau, Résidentiel, Commercial, Industriel, Mixte)
- ville
- surface_m2
- nombre_etages
- annee_construction
- certification_energetique (A, B, C, D, E)
- date_debut, date_fin, est_actuel (SCD Type 2)

**SCD Type 2**: Historique des changements de type, surface, certification

### dim_client

**Rôle**: Clients de GreenCity

**Attributs**:
- id_client (PK, surrogate key)
- code_client (Business key)
- type_client (Particulier, Entreprise, Administration)
- nom, prenom
- raison_sociale
- segment_client (Premium, Standard, Économique)
- ville
- date_debut, date_fin, est_actuel (SCD Type 2)

**SCD Type 2**: Historique des changements de segment

### dim_type_energie

**Rôle**: Types d'énergie

**Attributs**:
- id_type_energie (PK)
- nom_energie (Électricité, Eau, Gaz)
- unite_mesure (kWh, m3)
- facteur_emission_co2 (kg CO2 par unité)
- categorie (Énergie, Ressource)

**SCD Type 1**: Pas d'historique (mise à jour directe)

---

## Considérations de conception

### Choix du grain

**Consommation**: Horaire
- Permet l'analyse fine des profils de charge
- Peut être agrégé en journalier, mensuel, annuel
- Volume important mais gérable

**Rentabilité**: Facture
- Grain naturel du processus métier
- Une facture peut couvrir plusieurs périodes
- Lien avec les paiements

**Environnement**: Mensuel
- Fréquence des rapports environnementaux
- Suffisant pour l'analyse des tendances
- Volume réduit

### Gestion des dimensions à évolution lente (SCD)

**Type 1** (Écrasement):
- dim_type_energie: Les changements sont rares et non critiques

**Type 2** (Historisation):
- dim_region: Changements de population, zone climatique
- dim_batiment: Changements de type, certification
- dim_client: Changements de segment
- dim_compteur: Changements de statut, maintenance

**Avantages Type 2**:
- Historique complet des changements
- Analyse "as-was" possible
- Audit trail

**Inconvénients Type 2**:
- Augmentation du volume
- Complexité des requêtes (filtrer sur est_actuel)

### Mesures additives vs non-additives

**Additives** (peuvent être sommées sur toutes les dimensions):
- consommation_kwh
- montant_ttc
- emission_co2_kg

**Semi-additives** (peuvent être sommées sur certaines dimensions):
- temperature_celsius (moyenne, pas somme)
- taux_recyclage (moyenne, pas somme)

**Non-additives** (ne peuvent pas être sommées):
- taux_marge (moyenne pondérée)
- ratio_co2_consommation (calculé)

### Optimisation des performances

**Index recommandés**:
```sql
-- Tables de faits
CREATE INDEX idx_fact_conso_date ON fact_consommation(id_date);
CREATE INDEX idx_fact_conso_batiment ON fact_consommation(id_batiment);
CREATE INDEX idx_fact_conso_region ON fact_consommation(id_region);

-- Tables de dimensions
CREATE INDEX idx_dim_batiment_region ON dim_batiment(id_region);
CREATE INDEX idx_dim_batiment_actuel ON dim_batiment(est_actuel);
```

**Partitionnement** (pour gros volumes):
```sql
-- Partitionner fact_consommation par mois
ALTER TABLE fact_consommation
PARTITION BY RANGE (id_date) (
    PARTITION p_2024_01 VALUES LESS THAN (20240201),
    PARTITION p_2024_02 VALUES LESS THAN (20240301),
    ...
);
```

**Vues matérialisées** (pour requêtes fréquentes):
```sql
-- Vue matérialisée: Consommation mensuelle par bâtiment
CREATE MATERIALIZED VIEW mv_conso_mensuelle AS
SELECT 
    id_batiment,
    YEAR(date) AS annee,
    MONTH(date) AS mois,
    SUM(consommation_normalisee) AS consommation_totale
FROM fact_consommation f
JOIN dim_date d ON f.id_date = d.id_date
GROUP BY id_batiment, annee, mois;
```

---

## Volumétrie estimée

### Hypothèses
- 50 bâtiments
- 500 compteurs
- Mesures horaires (24/jour)
- 1 an de données

### Volumes

**fact_consommation**:
- 500 compteurs × 24 heures × 365 jours = 4,380,000 lignes/an
- Taille: ~500 MB/an

**fact_rentabilite**:
- 5,000 factures/an
- Taille: ~5 MB/an

**fact_environnement**:
- 50 bâtiments × 12 mois = 600 lignes/an
- Taille: ~100 KB/an

**Dimensions**:
- dim_date: 4,000 lignes (2020-2030)
- dim_batiment: 100 lignes (avec historique)
- dim_region: 20 lignes (avec historique)
- dim_client: 400 lignes (avec historique)
- dim_compteur: 1,000 lignes (avec historique)
- Taille totale: ~5 MB

**Total**: ~505 MB/an

---

## Évolutions futures

### Extensions possibles

1. **Nouveaux Data Marts**:
   - Maintenance et pannes
   - Qualité de service
   - Prévisions et budgets

2. **Nouvelles dimensions**:
   - dim_fournisseur_energie
   - dim_contrat
   - dim_equipement

3. **Nouvelles mesures**:
   - Coût de maintenance
   - Indice de performance énergétique
   - Score de durabilité

4. **Agrégats**:
   - Pré-calculer les agrégations mensuelles/annuelles
   - Améliorer les performances des requêtes

---

## Références

- Kimball, R. & Ross, M. (2013). *The Data Warehouse Toolkit*
- Inmon, W. H. (2005). *Building the Data Warehouse*
- Best practices dimensionnelles: https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/

