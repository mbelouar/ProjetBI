-- ============================================================================
-- Script de population de la dimension temporelle dim_date
-- ============================================================================
-- Description: Génère toutes les dates de 2020 à 2030
-- ============================================================================

USE greencity_dw;

-- Procédure pour peupler dim_date
DELIMITER //

DROP PROCEDURE IF EXISTS populate_dim_date//

CREATE PROCEDURE populate_dim_date(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    DECLARE current_date DATE;
    DECLARE date_id INT;
    
    SET current_date = start_date;
    
    -- Vider la table si elle contient déjà des données
    TRUNCATE TABLE dim_date;
    
    WHILE current_date <= end_date DO
        -- Calculer l'ID (format YYYYMMDD)
        SET date_id = YEAR(current_date) * 10000 + MONTH(current_date) * 100 + DAY(current_date);
        
        INSERT INTO dim_date (
            id_date,
            date,
            jour,
            mois,
            annee,
            trimestre,
            semestre,
            nom_mois,
            nom_jour_semaine,
            jour_semaine,
            jour_annee,
            semaine_annee,
            est_weekend,
            est_jour_ferie,
            nom_jour_ferie,
            periode_mois,
            periode_trimestre,
            periode_annee,
            saison
        ) VALUES (
            date_id,
            current_date,
            DAY(current_date),
            MONTH(current_date),
            YEAR(current_date),
            QUARTER(current_date),
            CASE WHEN MONTH(current_date) <= 6 THEN 1 ELSE 2 END,
            
            -- Nom du mois en français
            CASE MONTH(current_date)
                WHEN 1 THEN 'Janvier'
                WHEN 2 THEN 'Février'
                WHEN 3 THEN 'Mars'
                WHEN 4 THEN 'Avril'
                WHEN 5 THEN 'Mai'
                WHEN 6 THEN 'Juin'
                WHEN 7 THEN 'Juillet'
                WHEN 8 THEN 'Août'
                WHEN 9 THEN 'Septembre'
                WHEN 10 THEN 'Octobre'
                WHEN 11 THEN 'Novembre'
                WHEN 12 THEN 'Décembre'
            END,
            
            -- Nom du jour en français (1=Lundi, 7=Dimanche)
            CASE DAYOFWEEK(current_date)
                WHEN 1 THEN 'Dimanche'
                WHEN 2 THEN 'Lundi'
                WHEN 3 THEN 'Mardi'
                WHEN 4 THEN 'Mercredi'
                WHEN 5 THEN 'Jeudi'
                WHEN 6 THEN 'Vendredi'
                WHEN 7 THEN 'Samedi'
            END,
            
            -- Jour de la semaine (1=Lundi, 7=Dimanche)
            CASE DAYOFWEEK(current_date)
                WHEN 1 THEN 7
                WHEN 2 THEN 1
                WHEN 3 THEN 2
                WHEN 4 THEN 3
                WHEN 5 THEN 4
                WHEN 6 THEN 5
                WHEN 7 THEN 6
            END,
            
            DAYOFYEAR(current_date),
            WEEK(current_date, 1),
            
            -- Est weekend
            CASE WHEN DAYOFWEEK(current_date) IN (1, 7) THEN TRUE ELSE FALSE END,
            
            -- Est jour férié (Maroc)
            CASE 
                -- Jours fériés fixes
                WHEN (MONTH(current_date) = 1 AND DAY(current_date) = 1) THEN TRUE
                WHEN (MONTH(current_date) = 1 AND DAY(current_date) = 11) THEN TRUE
                WHEN (MONTH(current_date) = 5 AND DAY(current_date) = 1) THEN TRUE
                WHEN (MONTH(current_date) = 7 AND DAY(current_date) = 30) THEN TRUE
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 14) THEN TRUE
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 20) THEN TRUE
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 21) THEN TRUE
                WHEN (MONTH(current_date) = 11 AND DAY(current_date) = 6) THEN TRUE
                WHEN (MONTH(current_date) = 11 AND DAY(current_date) = 18) THEN TRUE
                ELSE FALSE
            END,
            
            -- Nom du jour férié
            CASE 
                WHEN (MONTH(current_date) = 1 AND DAY(current_date) = 1) THEN 'Nouvel An'
                WHEN (MONTH(current_date) = 1 AND DAY(current_date) = 11) THEN 'Manifeste de l\'Indépendance'
                WHEN (MONTH(current_date) = 5 AND DAY(current_date) = 1) THEN 'Fête du Travail'
                WHEN (MONTH(current_date) = 7 AND DAY(current_date) = 30) THEN 'Fête du Trône'
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 14) THEN 'Journée Oued Ed-Dahab'
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 20) THEN 'Révolution du Roi et du Peuple'
                WHEN (MONTH(current_date) = 8 AND DAY(current_date) = 21) THEN 'Fête de la Jeunesse'
                WHEN (MONTH(current_date) = 11 AND DAY(current_date) = 6) THEN 'Marche Verte'
                WHEN (MONTH(current_date) = 11 AND DAY(current_date) = 18) THEN 'Fête de l\'Indépendance'
                ELSE NULL
            END,
            
            -- Période mois (YYYY-MM)
            DATE_FORMAT(current_date, '%Y-%m'),
            
            -- Période trimestre (YYYY-Q1)
            CONCAT(YEAR(current_date), '-Q', QUARTER(current_date)),
            
            -- Période année (YYYY)
            YEAR(current_date),
            
            -- Saison
            CASE 
                WHEN MONTH(current_date) IN (12, 1, 2) THEN 'Hiver'
                WHEN MONTH(current_date) IN (3, 4, 5) THEN 'Printemps'
                WHEN MONTH(current_date) IN (6, 7, 8) THEN 'Été'
                WHEN MONTH(current_date) IN (9, 10, 11) THEN 'Automne'
            END
        );
        
        SET current_date = DATE_ADD(current_date, INTERVAL 1 DAY);
    END WHILE;
    
END//

DELIMITER ;

-- Exécuter la procédure pour générer les dates de 2020 à 2030
CALL populate_dim_date('2020-01-01', '2030-12-31');

-- Vérifier les résultats
SELECT 
    'Dimension temporelle peuplée avec succès' AS message,
    COUNT(*) AS nombre_dates,
    MIN(date) AS date_min,
    MAX(date) AS date_max
FROM dim_date;

-- Afficher quelques exemples
SELECT * FROM dim_date WHERE annee = 2024 LIMIT 10;

-- Statistiques par année
SELECT 
    annee,
    COUNT(*) AS nb_jours,
    SUM(est_weekend) AS nb_weekends,
    SUM(est_jour_ferie) AS nb_jours_feries
FROM dim_date
GROUP BY annee
ORDER BY annee;

