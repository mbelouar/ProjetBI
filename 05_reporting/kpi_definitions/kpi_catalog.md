# Catalogue des KPI - GreenCity

## 📊 Data Mart 1: Consommation Énergétique

### KPI 1.1: Consommation Totale
**Description**: Quantité totale d'énergie consommée  
**Formule**: `SUM(consommation_normalisee)`  
**Unité**: kWh  
**Dimensions d'analyse**: Client, Bâtiment, Région, Période, Type d'énergie  
**Requête SQL**:
```sql
SELECT 
    SUM(consommation_normalisee) AS consommation_totale
FROM fact_consommation;
```

### KPI 1.2: Consommation Moyenne par Bâtiment
**Description**: Consommation moyenne par bâtiment  
**Formule**: `AVG(consommation_normalisee)`  
**Unité**: kWh  
**Dimensions d'analyse**: Type de bâtiment, Région, Période  
**Requête SQL**:
```sql
SELECT 
    b.nom_batiment,
    b.type_batiment,
    AVG(f.consommation_normalisee) AS consommation_moyenne
FROM fact_consommation f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
WHERE b.est_actuel = TRUE
GROUP BY b.nom_batiment, b.type_batiment
ORDER BY consommation_moyenne DESC;
```

### KPI 1.3: Évolution Mensuelle de la Consommation
**Description**: Tendance de la consommation dans le temps  
**Formule**: `SUM(consommation_normalisee)` par mois  
**Unité**: kWh  
**Visualisation**: Graphique en courbe  
**Requête SQL**:
```sql
SELECT 
    d.annee,
    d.mois,
    d.nom_mois,
    SUM(f.consommation_normalisee) AS consommation_totale
FROM fact_consommation f
JOIN dim_date d ON f.id_date = d.id_date
GROUP BY d.annee, d.mois, d.nom_mois
ORDER BY d.annee, d.mois;
```

### KPI 1.4: Top 10 Bâtiments Consommateurs
**Description**: Classement des bâtiments les plus consommateurs  
**Formule**: `SUM(consommation_normalisee)` par bâtiment  
**Unité**: kWh  
**Visualisation**: Graphique en barres  
**Requête SQL**:
```sql
SELECT 
    b.nom_batiment,
    r.nom_region,
    SUM(f.consommation_normalisee) AS consommation_totale,
    b.surface_m2,
    SUM(f.consommation_normalisee) / b.surface_m2 AS consommation_par_m2
FROM fact_consommation f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
JOIN dim_region r ON b.id_region = r.id_region
WHERE b.est_actuel = TRUE
GROUP BY b.nom_batiment, r.nom_region, b.surface_m2
ORDER BY consommation_totale DESC
LIMIT 10;
```

### KPI 1.5: Corrélation Consommation-Température
**Description**: Relation entre consommation et température  
**Formule**: Corrélation entre `consommation_normalisee` et `temperature_celsius`  
**Visualisation**: Scatter plot  
**Requête SQL**:
```sql
SELECT 
    f.temperature_celsius,
    AVG(f.consommation_normalisee) AS consommation_moyenne,
    COUNT(*) AS nb_mesures
FROM fact_consommation f
WHERE f.temperature_celsius IS NOT NULL
GROUP BY f.temperature_celsius
ORDER BY f.temperature_celsius;
```

### KPI 1.6: Consommation par Type d'Énergie
**Description**: Répartition de la consommation par type d'énergie  
**Formule**: `SUM(consommation_normalisee)` par type  
**Visualisation**: Graphique en secteurs  
**Requête SQL**:
```sql
SELECT 
    te.nom_energie,
    SUM(f.consommation_normalisee) AS consommation_totale,
    SUM(f.consommation_normalisee) * 100.0 / (
        SELECT SUM(consommation_normalisee) FROM fact_consommation
    ) AS pourcentage
FROM fact_consommation f
JOIN dim_type_energie te ON f.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie;
```

### KPI 1.7: Consommation par Région
**Description**: Consommation totale par région géographique  
**Formule**: `SUM(consommation_normalisee)` par région  
**Visualisation**: Carte géographique  
**Requête SQL**:
```sql
SELECT 
    r.nom_region,
    r.zone_climatique,
    SUM(f.consommation_normalisee) AS consommation_totale,
    COUNT(DISTINCT f.id_batiment) AS nb_batiments,
    SUM(f.consommation_normalisee) / COUNT(DISTINCT f.id_batiment) AS consommation_par_batiment
FROM fact_consommation f
JOIN dim_region r ON f.id_region = r.id_region
WHERE r.est_actuel = TRUE
GROUP BY r.nom_region, r.zone_climatique
ORDER BY consommation_totale DESC;
```

### KPI 1.8: Consommation Horaire (Profil de charge)
**Description**: Répartition de la consommation par heure de la journée  
**Formule**: `AVG(consommation_normalisee)` par heure  
**Visualisation**: Graphique en barres  
**Requête SQL**:
```sql
SELECT 
    f.id_heure,
    AVG(f.consommation_normalisee) AS consommation_moyenne,
    MIN(f.consommation_normalisee) AS consommation_min,
    MAX(f.consommation_normalisee) AS consommation_max
FROM fact_consommation f
GROUP BY f.id_heure
ORDER BY f.id_heure;
```

---

## 💰 Data Mart 2: Rentabilité Économique

### KPI 2.1: Chiffre d'Affaires (CA)
**Description**: Revenu total généré  
**Formule**: `SUM(montant_ttc)`  
**Unité**: MAD (Dirham marocain)  
**Dimensions d'analyse**: Client, Bâtiment, Région, Période, Type d'énergie  
**Requête SQL**:
```sql
SELECT 
    SUM(montant_ttc) AS chiffre_affaires
FROM fact_rentabilite;
```

### KPI 2.2: Marge Totale
**Description**: Bénéfice total  
**Formule**: `SUM(marge)` où `marge = montant_ttc - cout_energie`  
**Unité**: MAD  
**Requête SQL**:
```sql
SELECT 
    SUM(marge) AS marge_totale,
    SUM(montant_ttc) AS ca_total,
    SUM(marge) * 100.0 / SUM(montant_ttc) AS taux_marge_pourcent
FROM fact_rentabilite;
```

### KPI 2.3: Taux de Marge Moyen
**Description**: Pourcentage de marge moyen  
**Formule**: `AVG(taux_marge)` où `taux_marge = marge / montant_ttc`  
**Unité**: %  
**Requête SQL**:
```sql
SELECT 
    AVG(taux_marge) * 100 AS taux_marge_moyen_pourcent
FROM fact_rentabilite;
```

### KPI 2.4: Taux de Recouvrement
**Description**: Pourcentage de factures payées  
**Formule**: `COUNT(factures payées) / COUNT(factures totales) * 100`  
**Unité**: %  
**Requête SQL**:
```sql
SELECT 
    COUNT(*) AS nb_factures_total,
    SUM(CASE WHEN est_paye THEN 1 ELSE 0 END) AS nb_factures_payees,
    SUM(CASE WHEN est_paye THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS taux_recouvrement_pourcent,
    SUM(montant_ttc) AS montant_total,
    SUM(CASE WHEN est_paye THEN montant_paye ELSE 0 END) AS montant_recouvre,
    SUM(CASE WHEN est_paye THEN montant_paye ELSE 0 END) * 100.0 / SUM(montant_ttc) AS taux_recouvrement_montant_pourcent
FROM fact_rentabilite;
```

### KPI 2.5: Délai Moyen de Paiement
**Description**: Nombre moyen de jours entre facture et paiement  
**Formule**: `AVG(delai_paiement_jours)`  
**Unité**: Jours  
**Requête SQL**:
```sql
SELECT 
    AVG(delai_paiement_jours) AS delai_moyen_jours,
    MIN(delai_paiement_jours) AS delai_min,
    MAX(delai_paiement_jours) AS delai_max
FROM fact_rentabilite
WHERE est_paye = TRUE;
```

### KPI 2.6: Top 10 Clients Rentables
**Description**: Classement des clients les plus rentables  
**Formule**: `SUM(marge)` par client  
**Visualisation**: Graphique en barres  
**Requête SQL**:
```sql
SELECT 
    c.code_client,
    COALESCE(c.raison_sociale, CONCAT(c.nom, ' ', c.prenom)) AS nom_client,
    c.type_client,
    c.segment_client,
    COUNT(*) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale,
    AVG(f.taux_marge) * 100 AS taux_marge_moyen_pourcent,
    SUM(CASE WHEN f.est_paye THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS taux_paiement_pourcent
FROM fact_rentabilite f
JOIN dim_client c ON f.id_client = c.id_client
WHERE c.est_actuel = TRUE
GROUP BY c.code_client, nom_client, c.type_client, c.segment_client
ORDER BY marge_totale DESC
LIMIT 10;
```

### KPI 2.7: Rentabilité par Région
**Description**: Performance financière par région  
**Formule**: `SUM(marge)` par région  
**Visualisation**: Carte géographique  
**Requête SQL**:
```sql
SELECT 
    r.nom_region,
    COUNT(DISTINCT f.id_client) AS nb_clients,
    COUNT(DISTINCT f.id_batiment) AS nb_batiments,
    COUNT(*) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale,
    AVG(f.taux_marge) * 100 AS taux_marge_moyen_pourcent
FROM fact_rentabilite f
JOIN dim_region r ON f.id_region = r.id_region
WHERE r.est_actuel = TRUE
GROUP BY r.nom_region
ORDER BY marge_totale DESC;
```

### KPI 2.8: Rentabilité par Type d'Énergie
**Description**: Performance financière par type d'énergie  
**Formule**: `SUM(marge)` par type d'énergie  
**Visualisation**: Graphique en barres  
**Requête SQL**:
```sql
SELECT 
    te.nom_energie,
    COUNT(*) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale,
    AVG(f.taux_marge) * 100 AS taux_marge_moyen_pourcent
FROM fact_rentabilite f
JOIN dim_type_energie te ON f.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie
ORDER BY marge_totale DESC;
```

### KPI 2.9: Évolution Mensuelle du CA
**Description**: Tendance du chiffre d'affaires dans le temps  
**Formule**: `SUM(montant_ttc)` par mois  
**Visualisation**: Graphique en courbe  
**Requête SQL**:
```sql
SELECT 
    d.annee,
    d.mois,
    d.nom_mois,
    COUNT(*) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale
FROM fact_rentabilite f
JOIN dim_date d ON f.id_date_facture = d.id_date
GROUP BY d.annee, d.mois, d.nom_mois
ORDER BY d.annee, d.mois;
```

### KPI 2.10: Analyse des Retards de Paiement
**Description**: Factures en retard de paiement  
**Formule**: `COUNT(*)` et `SUM(montant_ttc)` où `est_en_retard = TRUE`  
**Requête SQL**:
```sql
SELECT 
    COUNT(*) AS nb_factures_en_retard,
    SUM(montant_ttc) AS montant_en_retard,
    AVG(retard_paiement_jours) AS retard_moyen_jours,
    MAX(retard_paiement_jours) AS retard_max_jours
FROM fact_rentabilite
WHERE est_en_retard = TRUE;
```

---

## 🌍 Data Mart 3: Impact Environnemental

### KPI 3.1: Émissions Totales de CO₂
**Description**: Quantité totale de CO₂ émise  
**Formule**: `SUM(emission_co2_kg)`  
**Unité**: kg CO₂  
**Dimensions d'analyse**: Bâtiment, Région, Période  
**Requête SQL**:
```sql
SELECT 
    SUM(emission_co2_kg) AS emission_totale_kg,
    SUM(emission_co2_kg) / 1000 AS emission_totale_tonnes
FROM fact_environnement;
```

### KPI 3.2: Taux de Recyclage Moyen
**Description**: Pourcentage moyen de recyclage  
**Formule**: `AVG(taux_recyclage) * 100`  
**Unité**: %  
**Requête SQL**:
```sql
SELECT 
    AVG(taux_recyclage) * 100 AS taux_recyclage_moyen_pourcent,
    MIN(taux_recyclage) * 100 AS taux_min,
    MAX(taux_recyclage) * 100 AS taux_max
FROM fact_environnement;
```

### KPI 3.3: Ratio CO₂/Consommation
**Description**: Intensité carbone de la consommation  
**Formule**: `AVG(ratio_co2_consommation)`  
**Unité**: kg CO₂ / kWh  
**Requête SQL**:
```sql
SELECT 
    AVG(ratio_co2_consommation) AS ratio_moyen,
    MIN(ratio_co2_consommation) AS ratio_min,
    MAX(ratio_co2_consommation) AS ratio_max
FROM fact_environnement;
```

### KPI 3.4: Évolution des Émissions de CO₂
**Description**: Tendance des émissions dans le temps  
**Formule**: `SUM(emission_co2_kg)` par mois  
**Visualisation**: Graphique en courbe  
**Requête SQL**:
```sql
SELECT 
    d.annee,
    d.mois,
    d.nom_mois,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.taux_recyclage) * 100 AS taux_recyclage_moyen,
    SUM(f.consommation_totale_kwh) AS consommation_totale
FROM fact_environnement f
JOIN dim_date d ON f.id_date = d.id_date
GROUP BY d.annee, d.mois, d.nom_mois
ORDER BY d.annee, d.mois;
```

### KPI 3.5: Top 10 Bâtiments Polluants
**Description**: Classement des bâtiments les plus polluants  
**Formule**: `SUM(emission_co2_kg)` par bâtiment  
**Visualisation**: Graphique en barres  
**Requête SQL**:
```sql
SELECT 
    b.nom_batiment,
    b.type_batiment,
    r.nom_region,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.taux_recyclage) * 100 AS taux_recyclage_moyen,
    AVG(f.ratio_co2_consommation) AS ratio_co2_moyen,
    b.surface_m2,
    SUM(f.emission_co2_kg) / b.surface_m2 AS emission_par_m2
FROM fact_environnement f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
JOIN dim_region r ON b.id_region = r.id_region
WHERE b.est_actuel = TRUE
GROUP BY b.nom_batiment, b.type_batiment, r.nom_region, b.surface_m2
ORDER BY emission_totale DESC
LIMIT 10;
```

### KPI 3.6: Performance Environnementale par Région
**Description**: Impact environnemental par région  
**Formule**: `SUM(emission_co2_kg)` et `AVG(taux_recyclage)` par région  
**Visualisation**: Carte géographique  
**Requête SQL**:
```sql
SELECT 
    r.nom_region,
    r.zone_climatique,
    COUNT(DISTINCT f.id_batiment) AS nb_batiments,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.taux_recyclage) * 100 AS taux_recyclage_moyen,
    AVG(f.ratio_co2_consommation) AS ratio_co2_moyen,
    SUM(f.consommation_totale_kwh) AS consommation_totale
FROM fact_environnement f
JOIN dim_region r ON f.id_region = r.id_region
WHERE r.est_actuel = TRUE
GROUP BY r.nom_region, r.zone_climatique
ORDER BY emission_totale DESC;
```

### KPI 3.7: Variation Mensuelle des Émissions
**Description**: Évolution des émissions par rapport au mois précédent  
**Formule**: `AVG(variation_emission_pourcent)`  
**Unité**: %  
**Requête SQL**:
```sql
SELECT 
    d.annee,
    d.mois,
    d.nom_mois,
    SUM(f.emission_co2_kg) AS emission_actuelle,
    SUM(f.emission_co2_mois_precedent) AS emission_precedente,
    AVG(f.variation_emission_pourcent) AS variation_moyenne_pourcent
FROM fact_environnement f
JOIN dim_date d ON f.id_date = d.id_date
WHERE f.emission_co2_mois_precedent IS NOT NULL
GROUP BY d.annee, d.mois, d.nom_mois
ORDER BY d.annee, d.mois;
```

### KPI 3.8: Conformité aux Normes Environnementales
**Description**: Pourcentage de bâtiments conformes  
**Formule**: `COUNT(est_conforme = TRUE) / COUNT(*) * 100`  
**Unité**: %  
**Requête SQL**:
```sql
SELECT 
    COUNT(*) AS nb_rapports_total,
    SUM(CASE WHEN est_conforme_norme THEN 1 ELSE 0 END) AS nb_conformes,
    SUM(CASE WHEN est_conforme_norme THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS taux_conformite_pourcent
FROM fact_environnement;
```

### KPI 3.9: Répartition par Niveau de Performance
**Description**: Distribution des bâtiments par niveau de performance environnementale  
**Formule**: `COUNT(*)` par `niveau_performance`  
**Visualisation**: Graphique en secteurs  
**Requête SQL**:
```sql
SELECT 
    niveau_performance,
    COUNT(*) AS nb_rapports,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_environnement) AS pourcentage
FROM fact_environnement
WHERE niveau_performance IS NOT NULL
GROUP BY niveau_performance
ORDER BY 
    CASE niveau_performance
        WHEN 'Excellent' THEN 1
        WHEN 'Bon' THEN 2
        WHEN 'Moyen' THEN 3
        WHEN 'Faible' THEN 4
    END;
```

### KPI 3.10: Comparaison Consommation vs Émissions
**Description**: Relation entre consommation énergétique et émissions de CO₂  
**Visualisation**: Scatter plot  
**Requête SQL**:
```sql
SELECT 
    b.nom_batiment,
    b.type_batiment,
    SUM(f.consommation_totale_kwh) AS consommation_totale,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.ratio_co2_consommation) AS ratio_moyen
FROM fact_environnement f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
WHERE b.est_actuel = TRUE
GROUP BY b.nom_batiment, b.type_batiment
ORDER BY consommation_totale DESC;
```

---

## 📈 KPI Transversaux (Multi-Data Marts)

### KPI T.1: Vue d'Ensemble Globale
**Description**: Indicateurs clés consolidés  
**Requête SQL**:
```sql
SELECT 
    (SELECT SUM(consommation_normalisee) FROM fact_consommation) AS consommation_totale_kwh,
    (SELECT SUM(montant_ttc) FROM fact_rentabilite) AS ca_total,
    (SELECT SUM(marge) FROM fact_rentabilite) AS marge_totale,
    (SELECT SUM(emission_co2_kg) FROM fact_environnement) AS emission_totale_kg,
    (SELECT AVG(taux_recyclage) * 100 FROM fact_environnement) AS taux_recyclage_moyen;
```

### KPI T.2: Performance Globale par Bâtiment
**Description**: Vue consolidée de tous les indicateurs par bâtiment  
**Requête SQL**:
```sql
SELECT 
    b.nom_batiment,
    b.type_batiment,
    r.nom_region,
    
    -- Consommation
    (SELECT SUM(consommation_normalisee) 
     FROM fact_consommation fc 
     WHERE fc.id_batiment = b.id_batiment) AS consommation_totale,
    
    -- Rentabilité
    (SELECT SUM(montant_ttc) 
     FROM fact_rentabilite fr 
     WHERE fr.id_batiment = b.id_batiment) AS ca_total,
    
    (SELECT SUM(marge) 
     FROM fact_rentabilite fr 
     WHERE fr.id_batiment = b.id_batiment) AS marge_totale,
    
    -- Environnement
    (SELECT SUM(emission_co2_kg) 
     FROM fact_environnement fe 
     WHERE fe.id_batiment = b.id_batiment) AS emission_totale,
    
    (SELECT AVG(taux_recyclage) * 100 
     FROM fact_environnement fe 
     WHERE fe.id_batiment = b.id_batiment) AS taux_recyclage_moyen
    
FROM dim_batiment b
JOIN dim_region r ON b.id_region = r.id_region
WHERE b.est_actuel = TRUE
ORDER BY b.nom_batiment;
```

---

## 📝 Notes d'Utilisation

### Filtres Recommandés
- **Période**: Année, Trimestre, Mois, Semaine
- **Région**: Toutes les régions ou sélection spécifique
- **Type de bâtiment**: Bureau, Résidentiel, Commercial, Industriel, Mixte
- **Type d'énergie**: Électricité, Eau, Gaz
- **Segment client**: Premium, Standard, Économique

### Fréquence de Rafraîchissement
- **Consommation**: Quotidien (données horaires agrégées)
- **Rentabilité**: Quotidien (nouvelles factures/paiements)
- **Environnement**: Mensuel (rapports mensuels)

### Seuils d'Alerte
- **Consommation**: Augmentation > 20% par rapport au mois précédent
- **Taux de recouvrement**: < 70%
- **Délai de paiement**: > 45 jours
- **Émissions CO₂**: Augmentation > 15% par rapport au mois précédent
- **Taux de recyclage**: < 50%

