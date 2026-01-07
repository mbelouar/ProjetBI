-- ============================================================================
-- Script de création de la base de données opérationnelle GreenCity
-- ============================================================================
-- Auteur: Équipe BI GreenCity
-- Date: Janvier 2026
-- Description: Base de données opérationnelle pour le système de facturation
--              et gestion des bâtiments intelligents
-- ============================================================================

-- Création de la base de données
DROP DATABASE IF EXISTS greencity_operational;
CREATE DATABASE greencity_operational CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE greencity_operational;

-- ============================================================================
-- TABLE: dim_regions
-- Description: Régions géographiques où sont situés les bâtiments
-- ============================================================================
CREATE TABLE dim_regions (
    id_region VARCHAR(10) PRIMARY KEY,
    nom_region VARCHAR(100) NOT NULL,
    pays VARCHAR(50) NOT NULL DEFAULT 'Maroc',
    zone_climatique VARCHAR(50),
    population INT,
    superficie_km2 DECIMAL(10,2),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_nom_region (nom_region),
    INDEX idx_pays (pays)
) ENGINE=InnoDB COMMENT='Régions géographiques';

-- ============================================================================
-- TABLE: dim_batiments
-- Description: Bâtiments intelligents gérés par GreenCity
-- ============================================================================
CREATE TABLE dim_batiments (
    id_batiment VARCHAR(10) PRIMARY KEY,
    nom_batiment VARCHAR(200) NOT NULL,
    id_region VARCHAR(10) NOT NULL,
    type_batiment ENUM('Bureau', 'Résidentiel', 'Commercial', 'Industriel', 'Mixte') NOT NULL,
    adresse VARCHAR(255),
    ville VARCHAR(100),
    code_postal VARCHAR(20),
    surface_m2 DECIMAL(10,2),
    nombre_etages INT,
    annee_construction YEAR,
    certification_energetique VARCHAR(20),
    statut ENUM('Actif', 'Inactif', 'En maintenance') DEFAULT 'Actif',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_region) REFERENCES dim_regions(id_region),
    
    -- Index
    INDEX idx_region (id_region),
    INDEX idx_type (type_batiment),
    INDEX idx_ville (ville),
    INDEX idx_statut (statut)
) ENGINE=InnoDB COMMENT='Bâtiments intelligents';

-- ============================================================================
-- TABLE: dim_clients
-- Description: Clients de GreenCity
-- ============================================================================
CREATE TABLE dim_clients (
    id_client VARCHAR(10) PRIMARY KEY,
    type_client ENUM('Particulier', 'Entreprise', 'Administration') NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    raison_sociale VARCHAR(200),
    email VARCHAR(150),
    telephone VARCHAR(20),
    adresse VARCHAR(255),
    ville VARCHAR(100),
    code_postal VARCHAR(20),
    date_inscription DATE,
    segment_client ENUM('Premium', 'Standard', 'Économique') DEFAULT 'Standard',
    statut ENUM('Actif', 'Inactif', 'Suspendu') DEFAULT 'Actif',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_type_client (type_client),
    INDEX idx_email (email),
    INDEX idx_segment (segment_client),
    INDEX idx_statut (statut)
) ENGINE=InnoDB COMMENT='Clients';

-- ============================================================================
-- TABLE: dim_types_energie
-- Description: Types d'énergie (électricité, eau, gaz)
-- ============================================================================
CREATE TABLE dim_types_energie (
    id_type_energie INT AUTO_INCREMENT PRIMARY KEY,
    nom_energie VARCHAR(50) NOT NULL UNIQUE,
    unite_mesure VARCHAR(10) NOT NULL,
    facteur_emission_co2 DECIMAL(8,4) COMMENT 'kg CO2 par unité',
    prix_unitaire_moyen DECIMAL(10,4),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='Types d\'énergie';

-- Insertion des types d'énergie
INSERT INTO dim_types_energie (nom_energie, unite_mesure, facteur_emission_co2, prix_unitaire_moyen) VALUES
('Électricité', 'kWh', 0.4500, 1.2500),
('Eau', 'm3', 0.0003, 8.5000),
('Gaz', 'm3', 2.3500, 0.8500);

-- ============================================================================
-- TABLE: dim_compteurs
-- Description: Compteurs installés dans les bâtiments
-- ============================================================================
CREATE TABLE dim_compteurs (
    id_compteur VARCHAR(20) PRIMARY KEY,
    numero_serie VARCHAR(50) UNIQUE,
    id_batiment VARCHAR(10) NOT NULL,
    id_type_energie INT NOT NULL,
    marque VARCHAR(50),
    modele VARCHAR(50),
    date_installation DATE,
    date_derniere_maintenance DATE,
    statut ENUM('Actif', 'Inactif', 'En panne', 'En maintenance') DEFAULT 'Actif',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_batiment) REFERENCES dim_batiments(id_batiment),
    FOREIGN KEY (id_type_energie) REFERENCES dim_types_energie(id_type_energie),
    
    -- Index
    INDEX idx_batiment (id_batiment),
    INDEX idx_type_energie (id_type_energie),
    INDEX idx_statut (statut)
) ENGINE=InnoDB COMMENT='Compteurs d\'énergie';

-- ============================================================================
-- TABLE: fact_factures
-- Description: Factures émises aux clients
-- ============================================================================
CREATE TABLE fact_factures (
    id_facture VARCHAR(20) PRIMARY KEY,
    numero_facture VARCHAR(50) UNIQUE NOT NULL,
    id_client VARCHAR(10) NOT NULL,
    id_batiment VARCHAR(10) NOT NULL,
    id_type_energie INT NOT NULL,
    date_facture DATE NOT NULL,
    date_echeance DATE NOT NULL,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    
    -- Montants
    consommation_quantite DECIMAL(12,2) NOT NULL,
    prix_unitaire DECIMAL(10,4) NOT NULL,
    montant_ht DECIMAL(12,2) NOT NULL,
    taux_tva DECIMAL(5,4) DEFAULT 0.2000,
    montant_tva DECIMAL(12,2) NOT NULL,
    montant_ttc DECIMAL(12,2) NOT NULL,
    cout_energie DECIMAL(12,2) COMMENT 'Coût d\'achat de l\'énergie',
    
    -- Statut
    statut_facture ENUM('Émise', 'Envoyée', 'Payée', 'En retard', 'Annulée') DEFAULT 'Émise',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_client) REFERENCES dim_clients(id_client),
    FOREIGN KEY (id_batiment) REFERENCES dim_batiments(id_batiment),
    FOREIGN KEY (id_type_energie) REFERENCES dim_types_energie(id_type_energie),
    
    -- Index
    INDEX idx_client (id_client),
    INDEX idx_batiment (id_batiment),
    INDEX idx_date_facture (date_facture),
    INDEX idx_statut (statut_facture),
    INDEX idx_periode (periode_debut, periode_fin)
) ENGINE=InnoDB COMMENT='Factures';

-- ============================================================================
-- TABLE: fact_paiements
-- Description: Paiements reçus des clients
-- ============================================================================
CREATE TABLE fact_paiements (
    id_paiement VARCHAR(20) PRIMARY KEY,
    id_facture VARCHAR(20) NOT NULL,
    date_paiement DATE NOT NULL,
    montant_paye DECIMAL(12,2) NOT NULL,
    mode_paiement ENUM('Virement', 'Carte bancaire', 'Chèque', 'Espèces', 'Prélèvement') NOT NULL,
    reference_transaction VARCHAR(100),
    statut_paiement ENUM('Validé', 'En attente', 'Rejeté', 'Remboursé') DEFAULT 'Validé',
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_facture) REFERENCES fact_factures(id_facture),
    
    -- Index
    INDEX idx_facture (id_facture),
    INDEX idx_date_paiement (date_paiement),
    INDEX idx_mode_paiement (mode_paiement)
) ENGINE=InnoDB COMMENT='Paiements';

-- ============================================================================
-- TABLE: fact_meteo
-- Description: Données météorologiques par région
-- ============================================================================
CREATE TABLE fact_meteo (
    id_meteo BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_region VARCHAR(10) NOT NULL,
    date_mesure DATE NOT NULL,
    heure_mesure TIME,
    temperature_celsius DECIMAL(5,2),
    humidite_pourcent DECIMAL(5,2),
    vitesse_vent_kmh DECIMAL(5,2),
    precipitation_mm DECIMAL(6,2),
    ensoleillement_heures DECIMAL(4,2),
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (id_region) REFERENCES dim_regions(id_region),
    
    -- Index
    UNIQUE KEY uk_region_date_heure (id_region, date_mesure, heure_mesure),
    INDEX idx_date (date_mesure)
) ENGINE=InnoDB COMMENT='Données météorologiques';

-- ============================================================================
-- TABLE: log_extraction
-- Description: Log des extractions ETL pour gestion incrémentale
-- ============================================================================
CREATE TABLE log_extraction (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    nom_table VARCHAR(100) NOT NULL,
    date_derniere_extraction TIMESTAMP NOT NULL,
    nombre_lignes_extraites INT,
    statut ENUM('Succès', 'Échec', 'Partiel') DEFAULT 'Succès',
    message_erreur TEXT,
    
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='Log des extractions ETL';

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue: Factures avec informations complètes
CREATE VIEW v_factures_complete AS
SELECT 
    f.id_facture,
    f.numero_facture,
    f.date_facture,
    f.date_echeance,
    c.nom AS client_nom,
    c.prenom AS client_prenom,
    c.type_client,
    b.nom_batiment,
    b.type_batiment,
    r.nom_region,
    te.nom_energie,
    f.consommation_quantite,
    te.unite_mesure,
    f.montant_ttc,
    f.cout_energie,
    (f.montant_ttc - f.cout_energie) AS marge,
    f.statut_facture,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM fact_paiements p 
            WHERE p.id_facture = f.id_facture 
            AND p.statut_paiement = 'Validé'
        ) THEN 'Payée'
        WHEN f.date_echeance < CURDATE() THEN 'En retard'
        ELSE 'En attente'
    END AS statut_paiement
FROM fact_factures f
JOIN dim_clients c ON f.id_client = c.id_client
JOIN dim_batiments b ON f.id_batiment = b.id_batiment
JOIN dim_regions r ON b.id_region = r.id_region
JOIN dim_types_energie te ON f.id_type_energie = te.id_type_energie;

-- Vue: Statistiques par bâtiment
CREATE VIEW v_stats_batiments AS
SELECT 
    b.id_batiment,
    b.nom_batiment,
    r.nom_region,
    COUNT(DISTINCT c.id_compteur) AS nb_compteurs,
    COUNT(DISTINCT f.id_facture) AS nb_factures,
    SUM(f.montant_ttc) AS ca_total,
    SUM(f.montant_ttc - f.cout_energie) AS marge_totale
FROM dim_batiments b
JOIN dim_regions r ON b.id_region = r.id_region
LEFT JOIN dim_compteurs c ON b.id_batiment = c.id_batiment
LEFT JOIN fact_factures f ON b.id_batiment = f.id_batiment
GROUP BY b.id_batiment, b.nom_batiment, r.nom_region;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

-- Afficher les tables créées
SHOW TABLES;

-- Afficher les statistiques
SELECT 
    'Base de données créée avec succès' AS message,
    COUNT(*) AS nombre_tables
FROM information_schema.tables
WHERE table_schema = 'greencity_operational';

