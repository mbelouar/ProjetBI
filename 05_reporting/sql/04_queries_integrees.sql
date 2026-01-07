-- ============================================================================
-- REQUÊTES INTÉGRÉES - VUES GLOBALES
-- ============================================================================
-- Requêtes combinant plusieurs Data Marts pour une vue d'ensemble
-- ============================================================================

-- 1. Tableau de bord global : Vue d'ensemble par région
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    r.pays AS 'Pays',
    
    -- Consommation
    COUNT(DISTINCT fc.id_batiment) AS 'Nb Bâtiments (Consommation)',
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)), 2) AS 'Consommation Totale (kWh)',
    
    -- Rentabilité
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(COALESCE(fr.montant_ttc, 0)), 2) AS 'CA TTC',
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS 'Marge Total',
    
    -- Environnement
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS 'Émissions CO2 (tonnes)',
    ROUND(AVG(COALESCE(fe.taux_recyclage, 0)) * 100, 2) AS 'Taux Recyclage Moyen (%)'
    
FROM dim_region r
LEFT JOIN fact_consommation fc ON r.id_region = fc.id_region AND r.est_actuel = TRUE
LEFT JOIN fact_rentabilite fr ON r.id_region = fr.id_region AND r.est_actuel = TRUE
LEFT JOIN fact_environnement fe ON r.id_region = fe.id_region AND r.est_actuel = TRUE
WHERE r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region, r.pays
ORDER BY SUM(COALESCE(fc.consommation_normalisee, 0)) DESC;

-- 2. Performance globale par type de bâtiment
-- ============================================================================
SELECT 
    b.type_batiment AS 'Type Bâtiment',
    COUNT(DISTINCT b.id_batiment) AS 'Nb Bâtiments',
    
    -- Consommation
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)), 2) AS 'Consommation Totale (kWh)',
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)) / COUNT(DISTINCT b.id_batiment), 2) AS 'Consommation/Bâtiment',
    
    -- Rentabilité
    ROUND(SUM(COALESCE(fr.montant_ttc, 0)), 2) AS 'CA TTC',
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS 'Marge Total',
    ROUND(AVG(COALESCE(fr.taux_marge, 0)), 2) AS 'Taux Marge Moyen (%)',
    
    -- Environnement
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS 'Émissions CO2 (tonnes)',
    ROUND(AVG(COALESCE(fe.taux_recyclage, 0)) * 100, 2) AS 'Taux Recyclage Moyen (%)'
    
FROM dim_batiment b
LEFT JOIN fact_consommation fc ON b.id_batiment = fc.id_batiment AND b.est_actuel = TRUE
LEFT JOIN fact_rentabilite fr ON b.id_batiment = fr.id_batiment AND b.est_actuel = TRUE
LEFT JOIN fact_environnement fe ON b.id_batiment = fe.id_batiment AND b.est_actuel = TRUE
WHERE b.est_actuel = TRUE
GROUP BY b.type_batiment
ORDER BY SUM(COALESCE(fr.marge, 0)) DESC;

-- 3. Ratio rentabilité / impact environnemental
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS 'Marge Total',
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS 'Émissions CO2 (tonnes)',
    CASE 
        WHEN SUM(COALESCE(fe.emission_co2_kg, 0)) > 0 
        THEN ROUND(SUM(COALESCE(fr.marge, 0)) / (SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000), 2)
        ELSE NULL
    END AS 'Marge par Tonne CO2'
FROM dim_region r
INNER JOIN fact_rentabilite fr ON r.id_region = fr.id_region AND r.est_actuel = TRUE
INNER JOIN fact_environnement fe ON r.id_region = fe.id_region AND r.est_actuel = TRUE
WHERE r.est_actuel = TRUE
GROUP BY r.id_region, r.nom_region
HAVING SUM(COALESCE(fe.emission_co2_kg, 0)) > 0
ORDER BY SUM(COALESCE(fr.marge, 0)) / (SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000) DESC;

-- 4. Analyse saisonnière globale (2024)
-- ============================================================================
SELECT 
    dd.saison AS 'Saison',
    COUNT(DISTINCT dd.periode_mois) AS 'Nb Mois',
    
    -- Consommation
    COUNT(DISTINCT fc.id_compteur) AS 'Nb Compteurs Actifs',
    ROUND(SUM(COALESCE(fc.consommation_normalisee, 0)), 2) AS 'Consommation Totale (kWh)',
    
    -- Rentabilité
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(COALESCE(fr.montant_ttc, 0)), 2) AS 'CA TTC',
    ROUND(SUM(COALESCE(fr.marge, 0)), 2) AS 'Marge Total',
    
    -- Environnement
    ROUND(SUM(COALESCE(fe.emission_co2_kg, 0)) / 1000, 2) AS 'Émissions CO2 (tonnes)'
    
FROM dim_date dd
LEFT JOIN fact_consommation fc ON dd.id_date = fc.id_date
LEFT JOIN fact_rentabilite fr ON dd.id_date = fr.id_date_facture
LEFT JOIN fact_environnement fe ON dd.id_date = fe.id_date
WHERE dd.annee = 2024
GROUP BY dd.saison
ORDER BY 
    CASE dd.saison
        WHEN 'Printemps' THEN 1
        WHEN 'Été' THEN 2
        WHEN 'Automne' THEN 3
        WHEN 'Hiver' THEN 4
    END;


