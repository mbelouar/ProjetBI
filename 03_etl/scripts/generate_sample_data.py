#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Script de génération de données de test pour GreenCity
============================================================================
Auteur: Équipe BI GreenCity
Date: Janvier 2026
Description: Génère des données de test pour:
             - Base de données MySQL opérationnelle
             - Fichiers JSON (consommation IoT)
             - Fichiers CSV (rapports environnementaux)
============================================================================
"""

import json
import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector
from pathlib import Path

# Configuration
fake = Faker('fr_FR')
Faker.seed(42)
random.seed(42)

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_DIR = BASE_DIR / "01_operational_sources" / "json"
CSV_DIR = BASE_DIR / "01_operational_sources" / "csv"

# Créer les répertoires s'ils n'existent pas
JSON_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR.mkdir(parents=True, exist_ok=True)

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'imane2002',  # Mot de passe MySQL
    'database': 'greencity_operational'
}

# Paramètres de génération
NB_REGIONS = 10
NB_BATIMENTS = 50
NB_CLIENTS = 200
NB_COMPTEURS = 500
NB_FACTURES = 5000
TAUX_PAIEMENT = 0.80  # 80% des factures sont payées

# Période de génération des données
DATE_DEBUT = datetime(2024, 1, 1)
DATE_FIN = datetime(2024, 12, 31)

# Taux de défauts de qualité
TAUX_VALEURS_MANQUANTES = 0.05  # 5%
TAUX_DOUBLONS = 0.02  # 2%
TAUX_ESPACES_INUTILES = 0.10  # 10%


class DataGenerator:
    """Générateur de données de test"""
    
    def __init__(self):
        self.regions = []
        self.batiments = []
        self.clients = []
        self.compteurs = []
        self.types_energie = ['Électricité', 'Eau', 'Gaz']
        
    def generer_regions(self, nb=NB_REGIONS):
        """Génère des régions"""
        print(f"Génération de {nb} régions...")
        regions = []
        villes_maroc = [
            'Casablanca', 'Rabat', 'Fès', 'Marrakech', 'Agadir',
            'Tanger', 'Meknès', 'Oujda', 'Kenitra', 'Tétouan'
        ]
        
        for i in range(nb):
            region = {
                'id_region': f'REG{i+1:02d}',
                'nom_region': villes_maroc[i] if i < len(villes_maroc) else fake.city(),
                'pays': 'Maroc',
                'zone_climatique': random.choice(['Méditerranéen', 'Continental', 'Saharien', 'Océanique']),
                'population': random.randint(100000, 5000000),
                'superficie_km2': round(random.uniform(100, 10000), 2)
            }
            regions.append(region)
        
        self.regions = regions
        return regions
    
    def generer_batiments(self, nb=NB_BATIMENTS):
        """Génère des bâtiments"""
        print(f"Génération de {nb} bâtiments...")
        batiments = []
        types = ['Bureau', 'Résidentiel', 'Commercial', 'Industriel', 'Mixte']
        
        for i in range(nb):
            region = random.choice(self.regions)
            batiment = {
                'id_batiment': f'BAT{i+1:03d}',
                'nom_batiment': f'Bâtiment {fake.company()}',
                'id_region': region['id_region'],
                'type_batiment': random.choice(types),
                'adresse': fake.street_address(),
                'ville': region['nom_region'],
                'code_postal': fake.postcode(),
                'surface_m2': round(random.uniform(500, 50000), 2),
                'nombre_etages': random.randint(1, 30),
                'annee_construction': random.randint(1980, 2024),
                'certification_energetique': random.choice(['A', 'B', 'C', 'D', 'E', None]),
                'statut': 'Actif'
            }
            batiments.append(batiment)
        
        self.batiments = batiments
        return batiments
    
    def generer_clients(self, nb=NB_CLIENTS):
        """Génère des clients"""
        print(f"Génération de {nb} clients...")
        clients = []
        
        for i in range(nb):
            type_client = random.choice(['Particulier', 'Entreprise', 'Administration'])
            
            if type_client == 'Particulier':
                client = {
                    'id_client': f'CLI{i+1:04d}',
                    'type_client': type_client,
                    'nom': fake.last_name(),
                    'prenom': fake.first_name(),
                    'raison_sociale': None,
                    'email': fake.email(),
                    'telephone': fake.phone_number(),
                    'adresse': fake.street_address(),
                    'ville': fake.city(),
                    'code_postal': fake.postcode(),
                    'date_inscription': fake.date_between(start_date='-5y', end_date='today'),
                    'segment_client': random.choice(['Premium', 'Standard', 'Économique']),
                    'statut': 'Actif'
                }
            else:
                company_name = fake.company()
                client = {
                    'id_client': f'CLI{i+1:04d}',
                    'type_client': type_client,
                    'nom': company_name,
                    'prenom': None,
                    'raison_sociale': company_name,
                    'email': fake.company_email(),
                    'telephone': fake.phone_number(),
                    'adresse': fake.street_address(),
                    'ville': fake.city(),
                    'code_postal': fake.postcode(),
                    'date_inscription': fake.date_between(start_date='-5y', end_date='today'),
                    'segment_client': random.choice(['Premium', 'Standard', 'Économique']),
                    'statut': 'Actif'
                }
            
            # Introduire des défauts de qualité
            if random.random() < TAUX_ESPACES_INUTILES:
                if client['nom']:
                    client['nom'] = f"  {client['nom']}  "
                if client['email']:
                    client['email'] = f" {client['email']} "
            
            clients.append(client)
        
        self.clients = clients
        return clients
    
    def generer_compteurs(self, nb=NB_COMPTEURS):
        """Génère des compteurs"""
        print(f"Génération de {nb} compteurs...")
        compteurs = []
        prefixes = {'Électricité': 'ELEC', 'Eau': 'EAU', 'Gaz': 'GAZ'}
        
        for i in range(nb):
            batiment = random.choice(self.batiments)
            type_energie = random.choice(self.types_energie)
            prefix = prefixes[type_energie]
            
            compteur = {
                'id_compteur': f'{prefix}_{i+1:04d}',
                'numero_serie': f'SN{fake.bothify(text="????-####-????").upper()}',
                'id_batiment': batiment['id_batiment'],
                'type_energie': type_energie,
                'marque': random.choice(['Siemens', 'Schneider', 'ABB', 'Legrand', 'Honeywell']),
                'modele': f'Model-{random.randint(100, 999)}',
                'date_installation': fake.date_between(start_date='-10y', end_date='today'),
                'date_derniere_maintenance': fake.date_between(start_date='-1y', end_date='today'),
                'statut': 'Actif'
            }
            compteurs.append(compteur)
        
        self.compteurs = compteurs
        return compteurs
    
    def generer_json_consommation(self, annee=2024):
        """Génère les fichiers JSON de consommation"""
        print(f"Génération des fichiers JSON de consommation pour {annee}...")
        
        # Grouper les compteurs par type d'énergie et région
        compteurs_par_type = {
            'Électricité': [],
            'Eau': [],
            'Gaz': []
        }
        
        for compteur in self.compteurs:
            compteurs_par_type[compteur['type_energie']].append(compteur)
        
        # Générer un fichier par mois et par type d'énergie
        for mois in range(1, 13):
            for type_energie, compteurs in compteurs_par_type.items():
                if not compteurs:
                    continue
                
                # Grouper par région
                regions_data = {}
                for compteur in compteurs:
                    batiment = next(b for b in self.batiments if b['id_batiment'] == compteur['id_batiment'])
                    region_id = batiment['id_region']
                    
                    if region_id not in regions_data:
                        regions_data[region_id] = []
                    
                    regions_data[region_id].append({
                        'compteur': compteur,
                        'batiment': batiment
                    })
                
                # Créer le fichier JSON pour chaque région
                for region_id, items in regions_data.items():
                    # Grouper par bâtiment
                    batiments_data = {}
                    for item in items:
                        bat_id = item['batiment']['id_batiment']
                        if bat_id not in batiments_data:
                            batiments_data[bat_id] = {
                                'batiment': item['batiment'],
                                'compteurs': []
                            }
                        batiments_data[bat_id]['compteurs'].append(item['compteur'])
                    
                    # Construire la structure JSON
                    json_data = {
                        'id_region': region_id,
                        'batiments': []
                    }
                    
                    for bat_id, bat_data in batiments_data.items():
                        batiment_json = {
                            'id_batiment': bat_id,
                            'type_energie': type_energie.lower(),
                            'unite': 'kWh' if type_energie == 'Électricité' else 'm3',
                            'date_generation': f'{annee}-{mois:02d}-15',
                            'mesures': []
                        }
                        
                        # Générer des mesures horaires pour quelques jours
                        nb_jours = random.randint(5, 10)  # Quelques jours par mois
                        for jour in range(1, nb_jours + 1):
                            date_mesure = datetime(annee, mois, min(jour, 28))
                            
                            for compteur in bat_data['compteurs']:
                                # Générer quelques mesures horaires
                                nb_heures = random.randint(3, 8)
                                for heure in range(8, 8 + nb_heures):
                                    date_heure = date_mesure.replace(hour=heure)
                                    
                                    # Générer une consommation réaliste
                                    if type_energie == 'Électricité':
                                        conso = round(random.uniform(50, 200), 1)
                                        cle_conso = 'consommation_kWh'
                                    else:
                                        conso = round(random.uniform(0.5, 10), 2)
                                        cle_conso = 'consommation_m3'
                                    
                                    mesure = {
                                        'compteur_id': compteur['id_compteur'],
                                        'date_mesure': date_heure.strftime('%Y-%m-%dT%H:%M:%S'),
                                        cle_conso: conso
                                    }
                                    
                                    # Introduire des défauts de qualité
                                    if random.random() < TAUX_VALEURS_MANQUANTES:
                                        mesure[cle_conso] = None
                                    
                                    batiment_json['mesures'].append(mesure)
                        
                        json_data['batiments'].append(batiment_json)
                    
                    # Sauvegarder le fichier
                    prefix = type_energie[:4].capitalize()
                    filename = f'{prefix}_consumption_{mois:02d}_{annee}.json'
                    filepath = JSON_DIR / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✓ {filename} créé ({len(json_data['batiments'])} bâtiments)")
    
    def generer_csv_environnement(self, annee=2024):
        """Génère les fichiers CSV des rapports environnementaux"""
        print(f"Génération des fichiers CSV environnementaux pour {annee}...")
        
        for mois in range(1, 13):
            filename = f'env_reports_{mois:02d}_{annee}.csv'
            filepath = CSV_DIR / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id_region', 'id_batiment', 'date_rapport', 'emission_CO2_kg', 'taux_recyclage']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for batiment in self.batiments:
                    # Date de fin de mois
                    if mois == 12:
                        date_rapport = datetime(annee, mois, 31)
                    else:
                        date_rapport = datetime(annee, mois + 1, 1) - timedelta(days=1)
                    
                    # Générer des valeurs réalistes
                    surface = batiment['surface_m2']
                    emission_co2 = round(random.uniform(0.5, 2.0) * surface, 0)  # kg CO2
                    taux_recyclage = round(random.uniform(0.3, 0.9), 2)
                    
                    row = {
                        'id_region': batiment['id_region'],
                        'id_batiment': batiment['id_batiment'],
                        'date_rapport': date_rapport.strftime('%Y-%m-%d'),
                        'emission_CO2_kg': emission_co2,
                        'taux_recyclage': taux_recyclage
                    }
                    
                    # Introduire des défauts de qualité
                    if random.random() < TAUX_VALEURS_MANQUANTES:
                        row['emission_CO2_kg'] = ''
                    
                    if random.random() < TAUX_ESPACES_INUTILES:
                        row['id_region'] = f"  {row['id_region']}  "
                    
                    # Format de date varié (défaut de qualité)
                    if random.random() < 0.1:
                        row['date_rapport'] = date_rapport.strftime('%d/%m/%Y')  # Format EU
                    elif random.random() < 0.1:
                        row['date_rapport'] = date_rapport.strftime('%m/%d/%Y')  # Format US
                    
                    writer.writerow(row)
                    
                    # Introduire des doublons
                    if random.random() < TAUX_DOUBLONS:
                        writer.writerow(row)
            
            print(f"  ✓ {filename} créé ({len(self.batiments)} bâtiments)")
    
    def inserer_donnees_mysql(self):
        """Insère les données dans MySQL"""
        print("Insertion des données dans MySQL...")
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Insérer les régions
            print("  Insertion des régions...")
            for region in self.regions:
                sql = """
                INSERT INTO dim_regions (id_region, nom_region, pays, zone_climatique, population, superficie_km2)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    region['id_region'], region['nom_region'], region['pays'],
                    region['zone_climatique'], region['population'], region['superficie_km2']
                ))
            
            # Insérer les bâtiments
            print("  Insertion des bâtiments...")
            for batiment in self.batiments:
                sql = """
                INSERT INTO dim_batiments (id_batiment, nom_batiment, id_region, type_batiment,
                                          adresse, ville, code_postal, surface_m2, nombre_etages,
                                          annee_construction, certification_energetique, statut)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    batiment['id_batiment'], batiment['nom_batiment'], batiment['id_region'],
                    batiment['type_batiment'], batiment['adresse'], batiment['ville'],
                    batiment['code_postal'], batiment['surface_m2'], batiment['nombre_etages'],
                    batiment['annee_construction'], batiment['certification_energetique'],
                    batiment['statut']
                ))
            
            # Insérer les clients
            print("  Insertion des clients...")
            for client in self.clients:
                sql = """
                INSERT INTO dim_clients (id_client, type_client, nom, prenom, raison_sociale,
                                        email, telephone, adresse, ville, code_postal,
                                        date_inscription, segment_client, statut)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    client['id_client'], client['type_client'], client['nom'], client['prenom'],
                    client['raison_sociale'], client['email'], client['telephone'],
                    client['adresse'], client['ville'], client['code_postal'],
                    client['date_inscription'], client['segment_client'], client['statut']
                ))
            
            # Insérer les compteurs
            print("  Insertion des compteurs...")
            for compteur in self.compteurs:
                # Récupérer l'id_type_energie
                cursor.execute("SELECT id_type_energie FROM dim_types_energie WHERE nom_energie = %s",
                             (compteur['type_energie'],))
                id_type_energie = cursor.fetchone()[0]
                
                sql = """
                INSERT INTO dim_compteurs (id_compteur, numero_serie, id_batiment, id_type_energie,
                                          marque, modele, date_installation, date_derniere_maintenance, statut)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    compteur['id_compteur'], compteur['numero_serie'], compteur['id_batiment'],
                    id_type_energie, compteur['marque'], compteur['modele'],
                    compteur['date_installation'], compteur['date_derniere_maintenance'],
                    compteur['statut']
                ))
            
            # Générer et insérer des factures
            print(f"  Génération et insertion de {NB_FACTURES} factures...")
            self.generer_factures_mysql(cursor, NB_FACTURES)
            
            # Générer et insérer des données météo
            print("  Génération et insertion des données météo...")
            self.generer_meteo_mysql(cursor)
            
            conn.commit()
            print("✓ Données insérées avec succès dans MySQL")
            
        except mysql.connector.Error as err:
            print(f"✗ Erreur MySQL: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def generer_factures_mysql(self, cursor, nb_factures):
        """Génère des factures et paiements"""
        factures_generees = 0
        
        for i in range(nb_factures):
            client = random.choice(self.clients)
            batiment = random.choice(self.batiments)
            
            # Récupérer un compteur du bâtiment
            compteurs_batiment = [c for c in self.compteurs if c['id_batiment'] == batiment['id_batiment']]
            if not compteurs_batiment:
                continue
            
            compteur = random.choice(compteurs_batiment)
            
            # Récupérer l'id_type_energie
            cursor.execute("SELECT id_type_energie, prix_unitaire_moyen FROM dim_types_energie WHERE nom_energie = %s",
                         (compteur['type_energie'],))
            result = cursor.fetchone()
            if not result:
                continue
            id_type_energie, prix_unitaire = result
            
            # Générer une facture
            date_facture = fake.date_between(start_date=DATE_DEBUT, end_date=DATE_FIN)
            date_echeance = date_facture + timedelta(days=30)
            periode_debut = date_facture - timedelta(days=30)
            periode_fin = date_facture
            
            consommation = round(random.uniform(100, 5000), 2)
            prix = float(prix_unitaire) * (1 + random.uniform(-0.2, 0.2))  # Variation de prix
            montant_ht = round(consommation * prix, 2)
            taux_tva = 0.20
            montant_tva = round(montant_ht * taux_tva, 2)
            montant_ttc = montant_ht + montant_tva
            cout_energie = round(montant_ht * random.uniform(0.5, 0.8), 2)  # Coût d'achat
            
            id_facture = f'FACT{i+1:06d}'
            numero_facture = f'F-{date_facture.year}-{i+1:06d}'
            
            sql_facture = """
            INSERT INTO fact_factures (id_facture, numero_facture, id_client, id_batiment, id_type_energie,
                                      date_facture, date_echeance, periode_debut, periode_fin,
                                      consommation_quantite, prix_unitaire, montant_ht, taux_tva,
                                      montant_tva, montant_ttc, cout_energie, statut_facture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql_facture, (
                id_facture, numero_facture, client['id_client'], batiment['id_batiment'],
                id_type_energie, date_facture, date_echeance, periode_debut, periode_fin,
                consommation, prix, montant_ht, taux_tva, montant_tva, montant_ttc,
                cout_energie, 'Émise'
            ))
            
            factures_generees += 1
            
            # Générer un paiement (80% des factures)
            if random.random() < TAUX_PAIEMENT:
                delai = random.randint(1, 45)
                date_paiement = date_facture + timedelta(days=delai)
                
                # Paiement partiel ou total
                montant_paye = montant_ttc if random.random() < 0.9 else round(montant_ttc * random.uniform(0.5, 0.99), 2)
                
                id_paiement = f'PAY{i+1:06d}'
                mode_paiement = random.choice(['Virement', 'Carte bancaire', 'Chèque', 'Prélèvement'])
                
                sql_paiement = """
                INSERT INTO fact_paiements (id_paiement, id_facture, date_paiement, montant_paye,
                                           mode_paiement, reference_transaction, statut_paiement)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_paiement, (
                    id_paiement, id_facture, date_paiement, montant_paye,
                    mode_paiement, f'TRX-{fake.bothify(text="????-####").upper()}', 'Validé'
                ))
        
        print(f"    {factures_generees} factures générées")
    
    def generer_meteo_mysql(self, cursor):
        """Génère des données météorologiques"""
        nb_jours = (DATE_FIN - DATE_DEBUT).days + 1
        
        for region in self.regions:
            for jour in range(nb_jours):
                date_mesure = DATE_DEBUT + timedelta(days=jour)
                
                # Générer quelques mesures par jour
                for heure in [0, 6, 12, 18]:
                    temperature = round(random.uniform(5, 35), 1)
                    humidite = round(random.uniform(30, 90), 1)
                    vitesse_vent = round(random.uniform(0, 50), 1)
                    precipitation = round(random.uniform(0, 20), 1) if random.random() < 0.3 else 0
                    ensoleillement = round(random.uniform(0, 6), 1)
                    
                    sql = """
                    INSERT INTO fact_meteo (id_region, date_mesure, heure_mesure, temperature_celsius,
                                           humidite_pourcent, vitesse_vent_kmh, precipitation_mm, ensoleillement_heures)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE temperature_celsius = VALUES(temperature_celsius)
                    """
                    
                    cursor.execute(sql, (
                        region['id_region'], date_mesure, f'{heure:02d}:00:00',
                        temperature, humidite, vitesse_vent, precipitation, ensoleillement
                    ))


def main():
    """Fonction principale"""
    print("=" * 80)
    print("Génération des données de test pour GreenCity")
    print("=" * 80)
    print()
    
    generator = DataGenerator()
    
    # Générer les données
    generator.generer_regions()
    generator.generer_batiments()
    generator.generer_clients()
    generator.generer_compteurs()
    
    # Générer les fichiers JSON
    generator.generer_json_consommation(2024)
    
    # Générer les fichiers CSV
    generator.generer_csv_environnement(2024)
    
    # Insérer dans MySQL
    reponse = input("\nVoulez-vous insérer les données dans MySQL? (o/n): ")
    if reponse.lower() == 'o':
        generator.inserer_donnees_mysql()
    
    print()
    print("=" * 80)
    print("✓ Génération terminée avec succès!")
    print("=" * 80)
    print(f"\nFichiers JSON générés dans: {JSON_DIR}")
    print(f"Fichiers CSV générés dans: {CSV_DIR}")
    print()
    print("Statistiques:")
    print(f"  - Régions: {len(generator.regions)}")
    print(f"  - Bâtiments: {len(generator.batiments)}")
    print(f"  - Clients: {len(generator.clients)}")
    print(f"  - Compteurs: {len(generator.compteurs)}")
    print(f"  - Fichiers JSON: 36 (3 types × 12 mois)")
    print(f"  - Fichiers CSV: 12 (1 par mois)")


if __name__ == '__main__':
    main()

