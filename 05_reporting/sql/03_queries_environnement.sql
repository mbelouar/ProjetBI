-- ============================================================================
-- DATA MART 3: IMPACT ENVIRONNEMENTAL
-- ============================================================================
-- Requêtes SQL pour analyser l'impact environnemental
-- ============================================================================

-- 1. Vue d'ensemble des émissions CO2 par région
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    r.pays AS 'Pays',
    r.zone_climatique AS 'Zone Climatique',
    COUNT(DISTINCT fe.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 Total (kg)',
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS 'Émissions CO2 Total (tonnes)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)',
    ROUND(AVG(fe.ratio_co2_consommation), 4) AS 'Ratio CO2/Consommation Moyen'
FROM fact_environnement fe
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays, r.zone_climatique
ORDER BY SUM(fe.emission_co2_kg) DESC;

-- 2. Émissions CO2 mensuelles (2024)
-- ============================================================================
SELECT 
    dd.periode_mois AS 'Mois',
    dd.annee AS 'Année',
    COUNT(DISTINCT fe.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 (kg)',
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS 'Émissions CO2 (tonnes)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)'
FROM fact_environnement fe
INNER JOIN dim_date dd ON fe.id_date = dd.id_date
WHERE dd.annee = 2024
GROUP BY dd.periode_mois, dd.annee
ORDER BY dd.periode_mois;

-- 3. Top 10 des bâtiments les plus polluants
-- ============================================================================
SELECT 
    b.nom_batiment AS 'Bâtiment',
    b.type_batiment AS 'Type',
    r.nom_region AS 'Région',
    b.ville AS 'Ville',
    b.surface_m2 AS 'Surface (m2)',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 Total (kg)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(SUM(fe.emission_co2_kg) / b.surface_m2, 2) AS 'Émissions/m2 (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)'
FROM fact_environnement fe
INNER JOIN dim_batiment b ON fe.id_batiment = b.id_batiment AND b.est_actuel = TRUE
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region, b.ville, b.surface_m2
ORDER BY SUM(fe.emission_co2_kg) DESC
LIMIT 10;

-- 4. Analyse des émissions par type de bâtiment
-- ============================================================================
SELECT 
    b.type_batiment AS 'Type Bâtiment',
    COUNT(DISTINCT b.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 Total (kg)',
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS 'Émissions CO2 Total (tonnes)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(SUM(fe.emission_co2_kg) / COUNT(DISTINCT b.id_batiment), 2) AS 'Émissions/Bâtiment (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)'
FROM fact_environnement fe
INNER JOIN dim_batiment b ON fe.id_batiment = b.id_batiment AND b.est_actuel = TRUE
GROUP BY b.type_batiment
ORDER BY SUM(fe.emission_co2_kg) DESC;

-- 5. Taux de recyclage par région
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    r.pays AS 'Pays',
    COUNT(DISTINCT fe.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)',
    ROUND(MIN(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Min (%)',
    ROUND(MAX(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Max (%)',
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS 'Émissions CO2 Total (tonnes)'
FROM fact_environnement fe
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays
ORDER BY AVG(fe.taux_recyclage) DESC;

-- 6. Évolution trimestrielle des émissions CO2 (2024)
-- ============================================================================
SELECT 
    dd.periode_trimestre AS 'Trimestre',
    dd.annee AS 'Année',
    COUNT(DISTINCT fe.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 (kg)',
    ROUND(SUM(fe.emission_co2_kg) / 1000, 2) AS 'Émissions CO2 (tonnes)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)'
FROM fact_environnement fe
INNER JOIN dim_date dd ON fe.id_date = dd.id_date
WHERE dd.annee = 2024
GROUP BY dd.periode_trimestre, dd.annee
ORDER BY dd.periode_trimestre;

-- 7. Relation entre émissions et consommation énergétique
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions CO2 Moyennes (kg)',
    ROUND(AVG(fe.ratio_co2_consommation), 4) AS 'Ratio CO2/Consommation',
    COUNT(DISTINCT fe.id_batiment) AS 'Nb Bâtiments'
FROM fact_environnement fe
INNER JOIN dim_region r ON fe.id_region = r.id_region AND r.est_actuel = TRUE
WHERE fe.ratio_co2_consommation IS NOT NULL
GROUP BY r.id_region, r.nom_region
ORDER BY AVG(fe.ratio_co2_consommation) DESC;

-- 8. Analyse par certification énergétique
-- ============================================================================
SELECT 
    COALESCE(b.certification_energetique, 'Non renseignée') AS 'Certification',
    COUNT(DISTINCT b.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Rapports',
    ROUND(SUM(fe.emission_co2_kg), 2) AS 'Émissions CO2 Total (kg)',
    ROUND(AVG(fe.emission_co2_kg), 2) AS 'Émissions Moyennes (kg)',
    ROUND(SUM(fe.emission_co2_kg) / COUNT(DISTINCT b.id_batiment), 2) AS 'Émissions/Bâtiment (kg)',
    ROUND(AVG(fe.taux_recyclage) * 100, 2) AS 'Taux Recyclage Moyen (%)'
FROM fact_environnement fe
INNER JOIN dim_batiment b ON fe.id_batiment = b.id_batiment AND b.est_actuel = TRUE
GROUP BY b.certification_energetique
ORDER BY AVG(fe.emission_co2_kg);


