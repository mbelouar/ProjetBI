# 📋 Requêtes SQL Prêtes pour Power BI

Copier-coller ces requêtes dans Power BI Desktop pour créer des tables optimisées.

## 🔧 Comment Utiliser

1. **Power BI Desktop** → **Obtenir les données** → **Base de données MySQL**
2. **Navigateur** → **Code avancé**
3. **Coller la requête** souhaitée
4. **Nommer la table**
5. **Cliquer sur OK**

---

## 📊 Tableau de Bord Principal

### Requête 1 : KPIs Principaux

```sql
SELECT 
    -- Consommation
    (SELECT ROUND(SUM(consommation_normalisee), 2) FROM fact_consommation) AS Consommation_Total_kWh,
    
    -- Rentabilité
    (SELECT ROUND(SUM(montant_ttc), 2) FROM fact_rentabilite) AS CA_Total_EUR,
    (SELECT ROUND(SUM(marge), 2) FROM fact_rentabilite) AS Marge_Total_EUR,
    
    -- Environnement
    (SELECT ROUND(SUM(emission_co2_kg) / 1000, 2) FROM fact_environnement) AS Emissions_CO2_Tonnes,
    (SELECT ROUND(AVG(taux_recyclage) * 100, 2) FROM fact_environnement) AS Taux_Recyclage_Moyen
```

---

## 📈 Dashboard Consommation

### Requête 2 : Consommation par Type d'Énergie

```sql
SELECT 
    te.nom_energie AS Type_Energie,
    te.unite_mesure AS Unite,
    COUNT(*) AS Nb_Mesures,
    ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_Totale_kWh,
    ROUND(AVG(fc.consommation_normalisee), 2) AS Consommation_Moyenne_kWh,
    ROUND(MIN(fc.consommation_normalisee), 2) AS Consommation_Min_kWh,
    ROUND(MAX(fc.consommation_normalisee), 2) AS Consommation_Max_kWh
FROM fact_consommation fc
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie, te.unite_mesure
ORDER BY SUM(fc.consommation_normalisee) DESC
```

### Requête 3 : Consommation Mensuelle par Type

```sql
SELECT 
    dd.periode_mois AS Mois,
    dd.annee AS Annee,
    te.nom_energie AS Type_Energie,
    ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_kWh,
    COUNT(*) AS Nb_Mesures
FROM fact_consommation fc
INNER JOIN dim_date dd ON fc.id_date = dd.id_date
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
WHERE dd.annee = 2024
GROUP BY dd.periode_mois, dd.annee, te.nom_energie
ORDER BY dd.periode_mois, te.nom_energie
```

### Requête 4 : Top Bâtiments Consommateurs

```sql
SELECT 
    b.nom_batiment AS Batiment,
    b.type_batiment AS Type_Batiment,
    r.nom_region AS Region,
    b.ville AS Ville,
    b.surface_m2 AS Surface_m2,
    ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_Totale_kWh,
    ROUND(SUM(fc.consommation_normalisee) / b.surface_m2, 2) AS Consommation_par_m2
FROM fact_consommation fc
INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region, b.ville, b.surface_m2
ORDER BY SUM(fc.consommation_normalisee) DESC
LIMIT 20
```

### Requête 5 : Consommation par Région

```sql
SELECT 
    r.nom_region AS Region,
    r.pays AS Pays,
    r.zone_climatique AS Zone_Climatique,
    COUNT(DISTINCT fc.id_batiment) AS Nb_Batiments,
    ROUND(SUM(fc.consommation_normalisee), 2) AS Consommation_Totale_kWh,
    ROUND(AVG(fc.consommation_normalisee), 2) AS Consommation_Moyenne_kWh
FROM fact_consommation fc
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays, r.zone_climatique
ORDER BY SUM(fc.consommation_normalisee) DESC
```

---

## 💰 Dashboard Rentabilité

### Requête 6 : Vue d'Ensemble Rentabilité

```sql
SELECT 
    te.nom_energie AS Type_Energie,
    COUNT(DISTINCT fr.code_facture) AS Nb_Factures,
    COUNT(DISTINCT fr.id_client) AS Nb_Clients,
    ROUND(SUM(fr.montant_ht), 2) AS CA_HT,
    ROUND(SUM(fr.montant_tva), 2) AS TVA,
    ROUND(SUM(fr.montant_ttc), 2) AS CA_TTC,
    ROUND(SUM(fr.cout_energie), 2) AS Couts_Total,
    ROUND(SUM(fr.marge), 2) AS Marge_Total,
    ROUND(AVG(fr.taux_marge), 2) AS Taux_Marge_Moyen
FROM fact_rentabilite fr
INNER JOIN dim_type_energie te ON fr.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie
ORDER BY SUM(fr.montant_ttc) DESC
```

### Requête 7 : Rentabilité Mensuelle

```sql
SELECT 
    dd.periode_mois AS Mois,
    dd.annee AS Annee,
    r.nom_region AS Region,
    ROUND(SUM(fr.montant_ttc), 2) AS CA_TTC,
    ROUND(SUM(fr.cout_energie), 2) AS Couts,
    ROUND(SUM(fr.marge), 2) AS Marge,
    ROUND(AVG(fr.taux_marge), 2) AS Taux_Marge_Moyen
FROM fact_rentabilite fr
INNER JOIN dim_date dd ON fr.id_date_facture = dd.id_date
INNER JOIN dim_region r ON fr.id_region = r.id_region AND r.est_actuel = TRUE
WHERE dd.annee = 2024
GROUP BY dd.periode_mois, dd.annee, r.nom_region
ORDER BY dd.periode_mois, SUM(fr.montant_ttc) DESC
```

### Requête 8 : Top Clients

```sql
SELECT 
    c.type_client AS Type_Client,
    COALESCE(c.raison_sociale, CONCAT(c.nom, ' ', c.prenom)) AS Client,
    c.segment_client AS Segment,
    c.ville AS Ville,
    COUNT(DISTINCT fr.code_facture) AS Nb_Factures,
    ROUND(SUM(fr.montant_ttc), 2) AS CA_TTC_Total,
    ROUND(AVG(fr.montant_ttc), 2) AS Panier_Moyen,
    ROUND(SUM(fr.marge), 2) AS Marge_Total,
    ROUND(AVG(fr.taux_marge), 2) AS Taux_Marge_Moyen
FROM fact_rentabilite fr
INNER JOIN dim_client c ON fr.id_client = c.id_client AND c.est_actuel = TRUE
GROUP BY c.id_client, c.type_client, c.raison_sociale, c.nom, c.prenom, c.segment_client, c.ville
ORDER BY SUM(fr.montant_ttc) DESC
LIMIT 20
```

### Requête 9 : Analyse Délais de Paiement

```sql
SELECT 
    CASE 
        WHEN fr.delai_paiement_jours IS NULL THEN 'Non payé'
        WHEN fr.delai_paiement_jours <= 30 THEN '0-30 jours'
        WHEN fr.delai_paiement_jours <= 60 THEN '31-60 jours'
        WHEN fr.delai_paiement_jours <= 90 THEN '61-90 jours'
        ELSE '90+ jours'
    END AS Tranche_Delai,
    COUNT(DISTINCT fr.code_facture) AS Nb_Factures,
    ROUND(SUM(fr.montant_ttc), 2) AS Montant_TTC_Total,
    ROUND(AVG(fr.delai_paiement_jours), 1) AS Delai_Moyen_Jours,
    ROUND(SUM(fr.montant_restant), 2) AS Montant_Restant
FROM fact_rentabilite fr
GROUP BY 
    CASE 
        WHEN fr.delai_paiement_jours IS NULL THEN 'Non payé'
        WHEN fr.delai_paiement_jours <= 30 THEN '0-30 jours'
        WHEN fr.delai_paiement_jours <= 60 THEN '31-60 jours'
        WHEN fr.delai_paiement_jours <= 90 THEN '61-90 jours'
        ELSE '90+ jours'
    END
ORDER BY 
    CASE 
        WHEN fr.delai_paiement_jours IS NULL THEN 5
        WHEN fr.delai_paiement_jours <= 30 THEN 1
        WHEN fr.delai_paiement_jours <= 60 THEN 2
        WHEN fr.delai_paiement_jours <= 90 THEN 3
        ELSE 4
    END
```

---

## 🌱 Dashboard Environnement

### Requête 10 : Émissions CO2 par Région

```sql
SELECT 
    r.nom_region AS Region,
    r.pays AS Pays,
    r.zone_climatique AS Zone_Climatique,
    COUNT(DISTINCT fe.id_batiment) AS Nb_Batiments,
    COUNT(*) AS Nb_Rapports,
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS Emissions_CO2_Tonnes,
    ROUND(AVG(fe.emission_co2_kg), 2) AS Emissions_Moyennes_kg,
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS Taux_Recyclage_Moyen
FROM fact_environnement fe
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays, r.zone_climatique
ORDER BY SUM(fe.emission_co2_kg) DESC
```

### Requête 11 : Émissions Mensuelles

```sql
SELECT 
    dd.periode_mois AS Mois,
    dd.annee AS Annee,
    COUNT(DISTINCT fe.id_batiment) AS Nb_Batiments,
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS Emissions_CO2_Tonnes,
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS Taux_Recyclage_Moyen
FROM fact_environnement fe
INNER JOIN dim_date dd ON fe.id_date = dd.id_date
WHERE dd.annee = 2024
GROUP BY dd.periode_mois, dd.annee
ORDER BY dd.periode_mois
```

### Requête 12 : Top Bâtiments Polluants

```sql
SELECT 
    b.nom_batiment AS Batiment,
    b.type_batiment AS Type_Batiment,
    r.nom_region AS Region,
    b.surface_m2 AS Surface_m2,
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS Emissions_CO2_Tonnes,
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS Taux_Recyclage_Moyen
FROM fact_environnement fe
INNER JOIN dim_batiment b ON fe.id_batiment = b.id_batiment AND b.est_actuel = TRUE
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region, b.surface_m2
ORDER BY SUM(fe.emission_co2_kg) DESC
LIMIT 20
```

---

## 🌍 Requêtes Intégrées (Vue Globale)

### Requête 13 : Tableau de Bord Global par Région

```sql
SELECT 
    r.nom_region AS Region,
    r.pays AS Pays,
    
    -- Consommation
    COUNT(DISTINCT fc.id_batiment) AS Nb_Batiments_Consommation,
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)), 2) AS Consommation_Totale_kWh,
    
    -- Rentabilité
    COUNT(DISTINCT fr.code_facture) AS Nb_Factures,
    ROUND(SUM(COALESCE(fr.montant_ttc, 0)), 2) AS CA_TTC,
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS Marge_Total,
    
    -- Environnement
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS Emissions_CO2_Tonnes,
    ROUND(AVG(COALESCE(fe.taux_recyclage, 0)) * 100, 2) AS Taux_Recyclage_Moyen
    
FROM dim_region r
LEFT JOIN fact_consommation fc ON r.id_region = fc.id_region AND r.est_actuel = TRUE
LEFT JOIN fact_rentabilite fr ON r.id_region = fr.id_region AND r.est_actuel = TRUE
LEFT JOIN fact_environnement fe ON r.id_region = fe.id_region AND r.est_actuel = TRUE
WHERE r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays
ORDER BY SUM(COALESCE(fc.consommation_normalisee, 0)) DESC
```

### Requête 14 : Performance par Type de Bâtiment

```sql
SELECT 
    b.type_batiment AS Type_Batiment,
    COUNT(DISTINCT b.id_batiment) AS Nb_Batiments,
    
    -- Consommation
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)), 2) AS Consommation_Totale_kWh,
    
    -- Rentabilité
    ROUND(SUM(COALESCE(fr.montant_ttc, 0)), 2) AS CA_TTC,
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS Marge_Total,
    ROUND(AVG(COALESCE(fr.taux_marge, 0)), 2) AS Taux_Marge_Moyen,
    
    -- Environnement
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS Emissions_CO2_Tonnes
    
FROM dim_batiment b
LEFT JOIN fact_consommation fc ON b.id_batiment = fc.id_batiment AND b.est_actuel = TRUE
LEFT JOIN fact_rentabilite fr ON b.id_batiment = fr.id_batiment AND b.est_actuel = TRUE
LEFT JOIN fact_environnement fe ON b.id_batiment = fe.id_batiment AND b.est_actuel = TRUE
WHERE b.est_actuel = TRUE
GROUP BY b.type_batiment
ORDER BY SUM(COALESCE(fr.marge, 0)) DESC
```

---

## 💡 Astuces d'Utilisation

1. **Nommer les tables** : Donnez des noms clairs (ex: "Consommation par Type", "Top Clients")

2. **Utiliser comme table** : Chargez la requête comme table pour créer des visualisations

3. **Utiliser comme mesure** : Créez ensuite des mesures DAX pour des calculs supplémentaires

4. **Combiner avec DirectQuery** : Vous pouvez mélanger tables DirectQuery et tables importées

5. **Rafraîchir** : Les requêtes se rafraîchissent automatiquement (ou manuellement via "Actualiser")

---

**Prêt à créer vos dashboards ! 🚀**


