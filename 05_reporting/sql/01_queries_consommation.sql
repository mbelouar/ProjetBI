-- ============================================================================
-- DATA MART 1: CONSOMMATION ÉNERGÉTIQUE
-- ============================================================================
-- Requêtes SQL pour analyser la consommation énergétique
-- ============================================================================

-- 1. Vue d'ensemble de la consommation par type d'énergie
-- ============================================================================
SELECT 
    te.nom_energie AS 'Type Énergie',
    te.unite_mesure AS 'Unité',
    COUNT(DISTINCT fc.id_compteur) AS 'Nb Compteurs',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(COALESCE(fc.consommation_kwh, 0)), 2) AS 'Consommation kWh',
    ROUND(SUM(COALESCE(fc.consommation_m3, 0)), 2) AS 'Consommation m3',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Normalisée (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne par Mesure',
    ROUND(MIN(fc.consommation_normalisee), 2) AS 'Min',
    ROUND(MAX(fc.consommation_normalisee), 2) AS 'Max'
FROM fact_consommation fc
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie, te.unite_mesure
ORDER BY SUM(fc.consommation_normalisee) DESC;

-- 2. Consommation mensuelle par région et type d'énergie
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    r.pays AS 'Pays',
    te.nom_energie AS 'Type Énergie',
    dd.periode_mois AS 'Mois',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne (kWh)',
    ROUND(SUM(fc.consommation_normalisee) / COUNT(DISTINCT fc.id_batiment), 2) AS 'Consommation/Bâtiment'
FROM fact_consommation fc
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
INNER JOIN dim_date dd ON fc.id_date = dd.id_date
WHERE dd.annee = 2024
GROUP BY r.nom_region, r.pays, te.nom_energie, dd.periode_mois
ORDER BY dd.periode_mois, r.nom_region, te.nom_energie;

-- 3. Top 10 des bâtiments les plus consommateurs
-- ============================================================================
SELECT 
    b.nom_batiment AS 'Bâtiment',
    b.type_batiment AS 'Type',
    r.nom_region AS 'Région',
    b.ville AS 'Ville',
    b.surface_m2 AS 'Surface (m2)',
    COUNT(DISTINCT fc.id_type_energie) AS 'Nb Types Énergie',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(SUM(fc.consommation_normalisee) / b.surface_m2, 2) AS 'Consommation/m2'
FROM fact_consommation fc
INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region, b.ville, b.surface_m2
ORDER BY SUM(fc.consommation_normalisee) DESC
LIMIT 10;

-- 4. Consommation par type de bâtiment
-- ============================================================================
SELECT 
    b.type_batiment AS 'Type Bâtiment',
    COUNT(DISTINCT b.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne par Mesure',
    ROUND(SUM(fc.consommation_normalisee) / COUNT(DISTINCT b.id_batiment), 2) AS 'Consommation/Bâtiment'
FROM fact_consommation fc
INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
GROUP BY b.type_batiment
ORDER BY SUM(fc.consommation_normalisee) DESC;

-- 5. Évolution de la consommation trimestrielle (2024)
-- ============================================================================
SELECT 
    dd.periode_trimestre AS 'Trimestre',
    dd.annee AS 'Année',
    te.nom_energie AS 'Type Énergie',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne (kWh)'
FROM fact_consommation fc
INNER JOIN dim_date dd ON fc.id_date = dd.id_date
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
WHERE dd.annee = 2024
GROUP BY dd.periode_trimestre, dd.annee, te.nom_energie
ORDER BY dd.periode_trimestre, te.nom_energie;

-- 6. Consommation par zone climatique
-- ============================================================================
SELECT 
    r.zone_climatique AS 'Zone Climatique',
    COUNT(DISTINCT r.id_region) AS 'Nb Régions',
    COUNT(DISTINCT fc.id_batiment) AS 'Nb Bâtiments',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne (kWh)',
    ROUND(SUM(fc.consommation_normalisee) / COUNT(DISTINCT fc.id_batiment), 2) AS 'Consommation/Bâtiment'
FROM fact_consommation fc
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
WHERE r.zone_climatique IS NOT NULL AND r.zone_climatique != ''
GROUP BY r.zone_climatique
ORDER BY SUM(fc.consommation_normalisee) DESC;

-- 7. Comparaison consommation jour/semaine vs weekend
-- ============================================================================
SELECT 
    CASE 
        WHEN dd.est_weekend = TRUE THEN 'Weekend'
        ELSE 'Jour Semaine'
    END AS 'Type Jour',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne (kWh)'
FROM fact_consommation fc
INNER JOIN dim_date dd ON fc.id_date = dd.id_date
GROUP BY dd.est_weekend
ORDER BY dd.est_weekend;

-- 8. Consommation par certification énergétique
-- ============================================================================
SELECT 
    COALESCE(b.certification_energetique, 'Non renseignée') AS 'Certification',
    COUNT(DISTINCT b.id_batiment) AS 'Nb Bâtiments',
    COUNT(*) AS 'Nb Mesures',
    ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)',
    ROUND(AVG(fc.consommation_normalisee), 2) AS 'Moyenne (kWh)',
    ROUND(SUM(fc.consommation_normalisee) / COUNT(DISTINCT b.id_batiment), 2) AS 'Consommation/Bâtiment'
FROM fact_consommation fc
INNER JOIN dim_batiment b ON fc.id_batiment = b.id_batiment AND b.est_actuel = TRUE
GROUP BY b.certification_energetique
ORDER BY SUM(fc.consommation_normalisee) DESC;


