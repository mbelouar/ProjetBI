-- ============================================================================
-- Script de création du Data Warehouse GreenCity
-- ============================================================================
-- Auteur: Équipe BI GreenCity
-- Date: Janvier 2026
-- Description: Data Warehouse avec 3 Data Marts en architecture étoile
--              1. Consommation énergétique
--              2. Rentabilité économique
--              3. Impact environnemental
-- ============================================================================

-- Création de la base de données
DROP DATABASE IF EXISTS greencity_dw;
CREATE DATABASE greencity_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE greencity_dw;

-- ============================================================================
-- TABLES DE DIMENSIONS PARTAGÉES
-- ============================================================================

-- ============================================================================
-- DIMENSION: dim_date
-- Description: Dimension temporelle complète
-- ============================================================================
CREATE TABLE dim_date (
    id_date INT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    
    -- Composantes de la date
    jour INT NOT NULL,
    mois INT NOT NULL,
    annee INT NOT NULL,
    trimestre INT NOT NULL,
    semestre INT NOT NULL,
    
    -- Noms
    nom_mois VARCHAR(20),
    nom_jour_semaine VARCHAR(20),
    
    -- Indicateurs
    jour_semaine INT COMMENT '1=Lundi, 7=Dimanche',
    jour_annee INT,
    semaine_annee INT,
    est_weekend BOOLEAN,
    est_jour_ferie BOOLEAN,
    nom_jour_ferie VARCHAR(100),
    
    -- Périodes
    periode_mois VARCHAR(7) COMMENT 'YYYY-MM',
    periode_trimestre VARCHAR(7) COMMENT 'YYYY-Q1',
    periode_annee VARCHAR(4) COMMENT 'YYYY',
    
    -- Saison
    saison VARCHAR(20),
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_date (date),
    INDEX idx_annee_mois (annee, mois),
    INDEX idx_trimestre (annee, trimestre)
) ENGINE=InnoDB COMMENT='Dimension temporelle';

-- ============================================================================
-- DIMENSION: dim_region
-- Description: Régions géographiques
-- ============================================================================
CREATE TABLE dim_region (
    id_region INT AUTO_INCREMENT PRIMARY KEY,
    code_region VARCHAR(10) NOT NULL UNIQUE,
    nom_region VARCHAR(100) NOT NULL,
    pays VARCHAR(50) NOT NULL,
    zone_climatique VARCHAR(50),
    population INT,
    superficie_km2 DECIMAL(10,2),
    
    -- SCD Type 2
    date_debut DATE NOT NULL,
    date_fin DATE,
    est_actuel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_code_region (code_region),
    INDEX idx_actuel (est_actuel)
) ENGINE=InnoDB COMMENT='Dimension région';

-- ============================================================================
-- DIMENSION: dim_batiment
-- Description: Bâtiments intelligents
-- ============================================================================
CREATE TABLE dim_batiment (
    id_batiment INT AUTO_INCREMENT PRIMARY KEY,
    code_batiment VARCHAR(10) NOT NULL,
    nom_batiment VARCHAR(200) NOT NULL,
    id_region INT NOT NULL,
    type_batiment VARCHAR(50) NOT NULL,
    ville VARCHAR(100),
    surface_m2 DECIMAL(10,2),
    nombre_etages INT,
    annee_construction YEAR,
    certification_energetique VARCHAR(20),
    
    -- SCD Type 2
    date_debut DATE NOT NULL,
    date_fin DATE,
    est_actuel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_region) REFERENCES dim_region(id_region),
    
    -- Index
    INDEX idx_code_batiment (code_batiment),
    INDEX idx_region (id_region),
    INDEX idx_type (type_batiment),
    INDEX idx_actuel (est_actuel)
) ENGINE=InnoDB COMMENT='Dimension bâtiment';

-- ============================================================================
-- DIMENSION: dim_client
-- Description: Clients
-- ============================================================================
CREATE TABLE dim_client (
    id_client INT AUTO_INCREMENT PRIMARY KEY,
    code_client VARCHAR(10) NOT NULL,
    type_client VARCHAR(50) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    raison_sociale VARCHAR(200),
    segment_client VARCHAR(50),
    ville VARCHAR(100),
    
    -- SCD Type 2
    date_debut DATE NOT NULL,
    date_fin DATE,
    est_actuel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_code_client (code_client),
    INDEX idx_type (type_client),
    INDEX idx_segment (segment_client),
    INDEX idx_actuel (est_actuel)
) ENGINE=InnoDB COMMENT='Dimension client';

-- ============================================================================
-- DIMENSION: dim_compteur
-- Description: Compteurs d'énergie
-- ============================================================================
CREATE TABLE dim_compteur (
    id_compteur INT AUTO_INCREMENT PRIMARY KEY,
    code_compteur VARCHAR(20) NOT NULL,
    numero_serie VARCHAR(50),
    id_batiment INT NOT NULL,
    id_type_energie INT NOT NULL,
    marque VARCHAR(50),
    modele VARCHAR(50),
    date_installation DATE,
    
    -- SCD Type 2
    date_debut DATE NOT NULL,
    date_fin DATE,
    est_actuel BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_batiment) REFERENCES dim_batiment(id_batiment),
    
    -- Index
    INDEX idx_code_compteur (code_compteur),
    INDEX idx_batiment (id_batiment),
    INDEX idx_type_energie (id_type_energie),
    INDEX idx_actuel (est_actuel)
) ENGINE=InnoDB COMMENT='Dimension compteur';

-- ============================================================================
-- DIMENSION: dim_type_energie
-- Description: Types d'énergie
-- ============================================================================
CREATE TABLE dim_type_energie (
    id_type_energie INT AUTO_INCREMENT PRIMARY KEY,
    nom_energie VARCHAR(50) NOT NULL UNIQUE,
    unite_mesure VARCHAR(10) NOT NULL,
    facteur_emission_co2 DECIMAL(8,4) COMMENT 'kg CO2 par unité',
    categorie VARCHAR(50),
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='Dimension type énergie';

-- Insertion des types d'énergie
INSERT INTO dim_type_energie (nom_energie, unite_mesure, facteur_emission_co2, categorie) VALUES
('Électricité', 'kWh', 0.4500, 'Énergie'),
('Eau', 'm3', 0.0003, 'Ressource'),
('Gaz', 'm3', 2.3500, 'Énergie');

-- ============================================================================
-- DATA MART 1: CONSOMMATION ÉNERGÉTIQUE
-- ============================================================================

-- ============================================================================
-- TABLE DE FAITS: fact_consommation
-- Description: Mesures de consommation énergétique
-- Type: Transactionnel (grain = mesure horaire par compteur)
-- ============================================================================
CREATE TABLE fact_consommation (
    id_fait BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Clés étrangères (dimensions)
    id_date INT NOT NULL,
    id_heure INT NOT NULL COMMENT '0-23',
    id_batiment INT NOT NULL,
    id_compteur INT NOT NULL,
    id_region INT NOT NULL,
    id_client INT NOT NULL,
    id_type_energie INT NOT NULL,
    
    -- Mesures de consommation
    consommation_kwh DECIMAL(12,2) COMMENT 'Consommation en kWh (électricité)',
    consommation_m3 DECIMAL(12,2) COMMENT 'Consommation en m3 (eau, gaz)',
    consommation_normalisee DECIMAL(12,2) COMMENT 'Consommation convertie en kWh équivalent',
    
    -- Mesures de coût
    cout_unitaire DECIMAL(10,4),
    cout_total DECIMAL(12,2),
    
    -- Mesures contextuelles
    temperature_celsius DECIMAL(5,2),
    humidite_pourcent DECIMAL(5,2),
    
    -- Mesures calculées
    consommation_par_m2 DECIMAL(10,4) COMMENT 'Consommation / surface du bâtiment',
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_date) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_batiment) REFERENCES dim_batiment(id_batiment),
    FOREIGN KEY (id_compteur) REFERENCES dim_compteur(id_compteur),
    FOREIGN KEY (id_region) REFERENCES dim_region(id_region),
    FOREIGN KEY (id_client) REFERENCES dim_client(id_client),
    FOREIGN KEY (id_type_energie) REFERENCES dim_type_energie(id_type_energie),
    
    -- Index pour performance
    INDEX idx_date (id_date),
    INDEX idx_batiment (id_batiment),
    INDEX idx_region (id_region),
    INDEX idx_client (id_client),
    INDEX idx_type_energie (id_type_energie),
    INDEX idx_date_batiment (id_date, id_batiment),
    INDEX idx_date_region (id_date, id_region)
) ENGINE=InnoDB COMMENT='Fait consommation énergétique';

-- ============================================================================
-- DATA MART 2: RENTABILITÉ ÉCONOMIQUE
-- ============================================================================

-- ============================================================================
-- TABLE DE FAITS: fact_rentabilite
-- Description: Mesures de rentabilité économique
-- Type: Transactionnel (grain = facture)
-- ============================================================================
CREATE TABLE fact_rentabilite (
    id_fait BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Clés étrangères (dimensions)
    id_date_facture INT NOT NULL,
    id_date_echeance INT,
    id_date_paiement INT,
    id_batiment INT NOT NULL,
    id_client INT NOT NULL,
    id_region INT NOT NULL,
    id_type_energie INT NOT NULL,
    
    -- Identifiants métier
    code_facture VARCHAR(50) NOT NULL,
    code_paiement VARCHAR(50),
    
    -- Mesures de facturation
    consommation_quantite DECIMAL(12,2),
    prix_unitaire DECIMAL(10,4),
    montant_ht DECIMAL(12,2),
    montant_tva DECIMAL(12,2),
    montant_ttc DECIMAL(12,2),
    
    -- Mesures de coût
    cout_energie DECIMAL(12,2) COMMENT 'Coût d\'achat de l\'énergie',
    
    -- Mesures de rentabilité
    marge DECIMAL(12,2) COMMENT 'montant_ttc - cout_energie',
    taux_marge DECIMAL(7,4) COMMENT 'marge / montant_ttc',
    
    -- Mesures de paiement
    montant_paye DECIMAL(12,2),
    montant_restant DECIMAL(12,2),
    delai_paiement_jours INT COMMENT 'Nombre de jours entre facture et paiement',
    retard_paiement_jours INT COMMENT 'Nombre de jours de retard par rapport à l\'échéance',
    
    -- Indicateurs
    est_paye BOOLEAN DEFAULT FALSE,
    est_en_retard BOOLEAN DEFAULT FALSE,
    mode_paiement VARCHAR(50),
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_date_facture) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_date_echeance) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_date_paiement) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_batiment) REFERENCES dim_batiment(id_batiment),
    FOREIGN KEY (id_client) REFERENCES dim_client(id_client),
    FOREIGN KEY (id_region) REFERENCES dim_region(id_region),
    FOREIGN KEY (id_type_energie) REFERENCES dim_type_energie(id_type_energie),
    
    -- Index pour performance
    INDEX idx_date_facture (id_date_facture),
    INDEX idx_date_paiement (id_date_paiement),
    INDEX idx_batiment (id_batiment),
    INDEX idx_client (id_client),
    INDEX idx_region (id_region),
    INDEX idx_code_facture (code_facture),
    INDEX idx_est_paye (est_paye)
) ENGINE=InnoDB COMMENT='Fait rentabilité économique';

-- ============================================================================
-- DATA MART 3: IMPACT ENVIRONNEMENTAL
-- ============================================================================

-- ============================================================================
-- TABLE DE FAITS: fact_environnement
-- Description: Mesures d'impact environnemental
-- Type: Snapshot périodique (grain = rapport mensuel par bâtiment)
-- ============================================================================
CREATE TABLE fact_environnement (
    id_fait BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Clés étrangères (dimensions)
    id_date INT NOT NULL COMMENT 'Date du rapport (fin de mois)',
    id_batiment INT NOT NULL,
    id_region INT NOT NULL,
    
    -- Mesures environnementales
    emission_co2_kg DECIMAL(12,2) COMMENT 'Émissions de CO2 en kg',
    taux_recyclage DECIMAL(5,4) COMMENT 'Taux de recyclage (0-1)',
    
    -- Mesures de consommation (agrégées sur le mois)
    consommation_totale_kwh DECIMAL(12,2),
    consommation_electricite_kwh DECIMAL(12,2),
    consommation_eau_m3 DECIMAL(12,2),
    consommation_gaz_m3 DECIMAL(12,2),
    
    -- Mesures calculées
    ratio_co2_consommation DECIMAL(10,4) COMMENT 'kg CO2 / kWh',
    emission_co2_par_m2 DECIMAL(10,4) COMMENT 'kg CO2 / m2',
    
    -- Mesures comparatives
    emission_co2_mois_precedent DECIMAL(12,2),
    variation_emission_pourcent DECIMAL(7,4),
    taux_recyclage_mois_precedent DECIMAL(5,4),
    variation_recyclage_pourcent DECIMAL(7,4),
    
    -- Indicateurs
    est_conforme_norme BOOLEAN COMMENT 'Conforme aux normes environnementales',
    niveau_performance VARCHAR(20) COMMENT 'Excellent, Bon, Moyen, Faible',
    
    -- Métadonnées
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_date) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_batiment) REFERENCES dim_batiment(id_batiment),
    FOREIGN KEY (id_region) REFERENCES dim_region(id_region),
    
    -- Index pour performance
    UNIQUE KEY uk_date_batiment (id_date, id_batiment),
    INDEX idx_date (id_date),
    INDEX idx_batiment (id_batiment),
    INDEX idx_region (id_region),
    INDEX idx_date_region (id_date, id_region)
) ENGINE=InnoDB COMMENT='Fait impact environnemental';

-- ============================================================================
-- TABLES DE MÉTADONNÉES ETL
-- ============================================================================

-- ============================================================================
-- TABLE: etl_log
-- Description: Log des exécutions ETL
-- ============================================================================
CREATE TABLE etl_log (
    id_log BIGINT AUTO_INCREMENT PRIMARY KEY,
    nom_job VARCHAR(100) NOT NULL,
    nom_transformation VARCHAR(100),
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP,
    duree_secondes INT,
    statut ENUM('En cours', 'Succès', 'Échec', 'Avertissement') NOT NULL,
    nombre_lignes_lues INT,
    nombre_lignes_ecrites INT,
    nombre_lignes_rejetees INT,
    nombre_erreurs INT,
    message_erreur TEXT,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_date_debut (date_debut),
    INDEX idx_statut (statut),
    INDEX idx_nom_job (nom_job)
) ENGINE=InnoDB COMMENT='Log des exécutions ETL';

-- ============================================================================
-- TABLE: etl_qualite
-- Description: Contrôle qualité des données
-- ============================================================================
CREATE TABLE etl_qualite (
    id_controle BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_log BIGINT,
    nom_table VARCHAR(100) NOT NULL,
    type_controle VARCHAR(50) NOT NULL COMMENT 'Doublons, Valeurs manquantes, Cohérence, etc.',
    nombre_anomalies INT,
    description TEXT,
    
    -- Métadonnées
    date_controle TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_log) REFERENCES etl_log(id_log),
    
    -- Index
    INDEX idx_log (id_log),
    INDEX idx_table (nom_table),
    INDEX idx_type (type_controle)
) ENGINE=InnoDB COMMENT='Contrôle qualité ETL';

-- ============================================================================
-- VUES ANALYTIQUES
-- ============================================================================

-- Vue: Consommation par région et mois
CREATE VIEW v_consommation_region_mois AS
SELECT 
    d.annee,
    d.mois,
    d.nom_mois,
    r.nom_region,
    te.nom_energie,
    SUM(f.consommation_normalisee) AS consommation_totale,
    AVG(f.temperature_celsius) AS temperature_moyenne,
    COUNT(DISTINCT f.id_batiment) AS nombre_batiments
FROM fact_consommation f
JOIN dim_date d ON f.id_date = d.id_date
JOIN dim_region r ON f.id_region = r.id_region
JOIN dim_type_energie te ON f.id_type_energie = te.id_type_energie
GROUP BY d.annee, d.mois, d.nom_mois, r.nom_region, te.nom_energie;

-- Vue: Rentabilité par client
CREATE VIEW v_rentabilite_client AS
SELECT 
    c.code_client,
    c.nom,
    c.prenom,
    c.type_client,
    c.segment_client,
    COUNT(DISTINCT f.code_facture) AS nombre_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.marge) AS marge_totale,
    AVG(f.taux_marge) AS taux_marge_moyen,
    SUM(CASE WHEN f.est_paye THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS taux_paiement,
    AVG(f.delai_paiement_jours) AS delai_paiement_moyen
FROM fact_rentabilite f
JOIN dim_client c ON f.id_client = c.id_client
WHERE c.est_actuel = TRUE
GROUP BY c.code_client, c.nom, c.prenom, c.type_client, c.segment_client;

-- Vue: Impact environnemental par bâtiment
CREATE VIEW v_environnement_batiment AS
SELECT 
    b.code_batiment,
    b.nom_batiment,
    r.nom_region,
    d.annee,
    SUM(f.emission_co2_kg) AS emission_totale,
    AVG(f.taux_recyclage) AS taux_recyclage_moyen,
    AVG(f.ratio_co2_consommation) AS ratio_co2_moyen,
    SUM(f.consommation_totale_kwh) AS consommation_totale
FROM fact_environnement f
JOIN dim_batiment b ON f.id_batiment = b.id_batiment
JOIN dim_region r ON b.id_region = r.id_region
JOIN dim_date d ON f.id_date = d.id_date
WHERE b.est_actuel = TRUE
GROUP BY b.code_batiment, b.nom_batiment, r.nom_region, d.annee;

-- ============================================================================
-- PROCÉDURES STOCKÉES UTILES
-- ============================================================================

DELIMITER //

-- Procédure: Calculer les statistiques d'une table de faits
CREATE PROCEDURE sp_stats_table_faits(IN p_nom_table VARCHAR(100))
BEGIN
    SET @sql = CONCAT('SELECT 
        ''', p_nom_table, ''' AS table_name,
        COUNT(*) AS nombre_lignes,
        MIN(date_ajout) AS premiere_ligne,
        MAX(date_ajout) AS derniere_ligne
    FROM ', p_nom_table);
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

-- Afficher les tables créées
SHOW TABLES;

-- Afficher les statistiques
SELECT 
    'Data Warehouse créé avec succès' AS message,
    COUNT(*) AS nombre_tables
FROM information_schema.tables
WHERE table_schema = 'greencity_dw';

-- Afficher les tables de faits
SELECT 
    table_name,
    table_comment
FROM information_schema.tables
WHERE table_schema = 'greencity_dw'
AND table_name LIKE 'fact_%';

-- Afficher les dimensions
SELECT 
    table_name,
    table_comment
FROM information_schema.tables
WHERE table_schema = 'greencity_dw'
AND table_name LIKE 'dim_%';

