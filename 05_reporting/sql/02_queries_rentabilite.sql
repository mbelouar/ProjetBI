-- ============================================================================
-- DATA MART 2: RENTABILITÉ ÉCONOMIQUE
-- ============================================================================
-- Requêtes SQL pour analyser la rentabilité économique
-- ============================================================================

-- 1. Vue d'ensemble de la rentabilité par type d'énergie
-- ============================================================================
SELECT 
    te.nom_energie AS 'Type Énergie',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    COUNT(DISTINCT fr.id_client) AS 'Nb Clients',
    COUNT(DISTINCT fr.id_batiment) AS 'Nb Bâtiments',
    ROUND(SUM(fr.consommation_quantite), 2) AS 'Quantité Consommée',
    ROUND(AVG(fr.prix_unitaire), 4) AS 'Prix Unitaire Moyen',
    ROUND(SUM(fr.montant_ht), 2) AS 'CA HT Total',
    ROUND(SUM(fr.montant_tva), 2) AS 'TVA Total',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC Total',
    ROUND(SUM(fr.cout_energie), 2) AS 'Coût Total',
    ROUND(SUM(fr.marge), 2) AS 'Marge Total',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.montant_paye), 2) AS 'Montant Payé',
    ROUND(SUM(fr.montant_restant), 2) AS 'Montant Restant'
FROM fact_rentabilite fr
INNER JOIN dim_type_energie te ON fr.id_type_energie = te.id_type_energie
GROUP BY te.nom_energie
ORDER BY SUM(fr.montant_ttc) DESC;

-- 2. Rentabilité mensuelle par région
-- ============================================================================
SELECT 
    r.nom_region AS 'Région',
    dd.periode_mois AS 'Mois',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC',
    ROUND(SUM(fr.cout_energie), 2) AS 'Coûts',
    ROUND(SUM(fr.marge), 2) AS 'Marge',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.montant_paye) / SUM(fr.montant_ttc) * 100, 2) AS 'Taux Recouvrement (%)'
FROM fact_rentabilite fr
INNER JOIN dim_region r ON fr.id_region = r.id_region AND r.est_actuel = TRUE
INNER JOIN dim_date dd ON fr.id_date_facture = dd.id_date
WHERE dd.annee = 2024
GROUP BY r.nom_region, dd.periode_mois
ORDER BY dd.periode_mois, SUM(fr.montant_ttc) DESC;

-- 3. Top 10 des clients par chiffre d'affaires
-- ============================================================================
SELECT 
    c.type_client AS 'Type Client',
    COALESCE(c.raison_sociale, CONCAT(c.nom, ' ', c.prenom)) AS 'Client',
    c.segment_client AS 'Segment',
    c.ville AS 'Ville',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    COUNT(DISTINCT fr.id_batiment) AS 'Nb Bâtiments',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC Total',
    ROUND(AVG(fr.montant_ttc), 2) AS 'Panier Moyen',
    ROUND(SUM(fr.marge), 2) AS 'Marge Total',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.montant_paye) / SUM(fr.montant_ttc) * 100, 2) AS 'Taux Recouvrement (%)'
FROM fact_rentabilite fr
INNER JOIN dim_client c ON fr.id_client = c.id_client AND c.est_actuel = TRUE
GROUP BY c.id_client, c.type_client, c.raison_sociale, c.nom, c.prenom, c.segment_client, c.ville
ORDER BY SUM(fr.montant_ttc) DESC
LIMIT 10;

-- 4. Analyse de la rentabilité par type de bâtiment
-- ============================================================================
SELECT 
    b.type_batiment AS 'Type Bâtiment',
    COUNT(DISTINCT fr.id_batiment) AS 'Nb Bâtiments',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC Total',
    ROUND(SUM(fr.cout_energie), 2) AS 'Coûts Total',
    ROUND(SUM(fr.marge), 2) AS 'Marge Total',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.montant_ttc) / COUNT(DISTINCT fr.id_batiment), 2) AS 'CA/Bâtiment'
FROM fact_rentabilite fr
INNER JOIN dim_batiment b ON fr.id_batiment = b.id_batiment AND b.est_actuel = TRUE
GROUP BY b.type_batiment
ORDER BY SUM(fr.marge) DESC;

-- 5. Évolution trimestrielle du CA et de la marge (2024)
-- ============================================================================
SELECT 
    dd.periode_trimestre AS 'Trimestre',
    dd.annee AS 'Année',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC',
    ROUND(SUM(fr.cout_energie), 2) AS 'Coûts',
    ROUND(SUM(fr.marge), 2) AS 'Marge',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.marge) / LAG(SUM(fr.marge)) OVER (ORDER BY dd.periode_trimestre) * 100 - 100, 2) AS 'Évolution Marge (%)'
FROM fact_rentabilite fr
INNER JOIN dim_date dd ON fr.id_date_facture = dd.id_date
WHERE dd.annee = 2024
GROUP BY dd.periode_trimestre, dd.annee
ORDER BY dd.periode_trimestre;

-- 6. Analyse des délais de paiement
-- ============================================================================
SELECT 
    CASE 
        WHEN fr.delai_paiement_jours IS NULL THEN 'Non payé'
        WHEN fr.delai_paiement_jours <= 30 THEN '0-30 jours'
        WHEN fr.delai_paiement_jours <= 60 THEN '31-60 jours'
        WHEN fr.delai_paiement_jours <= 90 THEN '61-90 jours'
        ELSE '90+ jours'
    END AS 'Tranche Délai',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'Montant TTC Total',
    ROUND(AVG(fr.delai_paiement_jours), 1) AS 'Délai Moyen (jours)',
    ROUND(SUM(fr.montant_paye), 2) AS 'Montant Payé',
    ROUND(SUM(fr.montant_restant), 2) AS 'Montant Restant',
    COUNT(CASE WHEN fr.est_en_retard = TRUE THEN 1 END) AS 'Nb Factures en Retard'
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
    END;

-- 7. Top 10 des bâtiments les plus rentables
-- ============================================================================
SELECT 
    b.nom_batiment AS 'Bâtiment',
    b.type_batiment AS 'Type',
    r.nom_region AS 'Région',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC',
    ROUND(SUM(fr.marge), 2) AS 'Marge',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge (%)',
    ROUND(SUM(fr.marge) / b.surface_m2, 2) AS 'Marge/m2'
FROM fact_rentabilite fr
INNER JOIN dim_batiment b ON fr.id_batiment = b.id_batiment AND b.est_actuel = TRUE
INNER JOIN dim_region r ON fr.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY b.id_batiment, b.nom_batiment, b.type_batiment, r.nom_region, b.surface_m2
ORDER BY SUM(fr.marge) DESC
LIMIT 10;

-- 8. Analyse par segment client
-- ============================================================================
SELECT 
    c.segment_client AS 'Segment Client',
    COUNT(DISTINCT c.id_client) AS 'Nb Clients',
    COUNT(DISTINCT fr.code_facture) AS 'Nb Factures',
    ROUND(SUM(fr.montant_ttc), 2) AS 'CA TTC Total',
    ROUND(AVG(fr.montant_ttc), 2) AS 'Panier Moyen',
    ROUND(SUM(fr.marge), 2) AS 'Marge Total',
    ROUND(AVG(fr.taux_marge), 2) AS 'Taux Marge Moyen (%)',
    ROUND(SUM(fr.montant_paye) / SUM(fr.montant_ttc) * 100, 2) AS 'Taux Recouvrement (%)'
FROM fact_rentabilite fr
INNER JOIN dim_client c ON fr.id_client = c.id_client AND c.est_actuel = TRUE
WHERE c.segment_client IS NOT NULL AND c.segment_client != ''
GROUP BY c.segment_client
ORDER BY SUM(fr.montant_ttc) DESC;


