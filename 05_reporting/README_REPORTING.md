# 📊 Guide de Reporting BI - GreenCity

Ce guide explique comment utiliser les requêtes SQL et créer des visualisations pour les 3 Data Marts.

## 📁 Structure des Fichiers

```
05_reporting/
├── sql/
│   ├── 01_queries_consommation.sql    # Data Mart 1: Consommation Énergétique
│   ├── 02_queries_rentabilite.sql     # Data Mart 2: Rentabilité Économique
│   ├── 03_queries_environnement.sql   # Data Mart 3: Impact Environnemental
│   └── 04_queries_integrees.sql       # Requêtes intégrées (vue globale)
└── README_REPORTING.md                 # Ce fichier
```

## 🚀 Comment Utiliser ces Requêtes

### Option 1: MySQL Workbench / MySQL CLI

1. **Connexion au Data Warehouse**
   ```bash
   mysql -h localhost -u root -p greencity_dw
   ```

2. **Exécuter une requête**
   ```sql
   USE greencity_dw;
   SOURCE 05_reporting/sql/01_queries_consommation.sql;
   ```

### Option 2: Outil de Visualisation (Power BI, Tableau, etc.)

1. **Connexion au Data Warehouse MySQL**
   - Hôte: `localhost`
   - Port: `3306`
   - Base de données: `greencity_dw`
   - Utilisateur: `root` (ou selon votre config)

2. **Importer les requêtes SQL** dans votre outil

3. **Créer des visualisations** (voir section ci-dessous)

### Option 3: Python (Pandas + Matplotlib/Plotly)

Voir `05_reporting/python/visualizations.py` (à créer)

## 📈 Requêtes Disponibles par Data Mart

### Data Mart 1: Consommation Énergétique

**Fichier**: `01_queries_consommation.sql`

1. **Vue d'ensemble par type d'énergie**
   - Consommation totale, moyenne, min, max par type d'énergie

2. **Consommation mensuelle par région**
   - Évolution temporelle de la consommation

3. **Top 10 bâtiments consommateurs**
   - Identifie les bâtiments les plus énergivores

4. **Consommation par type de bâtiment**
   - Compare les différents types (résidentiel, commercial, etc.)

5. **Évolution trimestrielle**
   - Tendances saisonnières

6. **Consommation par zone climatique**
   - Impact du climat sur la consommation

7. **Comparaison jour/semaine vs weekend**
   - Patterns de consommation

8. **Impact de la certification énergétique**
   - Efficacité des certifications

### Data Mart 2: Rentabilité Économique

**Fichier**: `02_queries_rentabilite.sql`

1. **Vue d'ensemble par type d'énergie**
   - CA, marge, taux de marge

2. **Rentabilité mensuelle par région**
   - Performance financière par région

3. **Top 10 clients par CA**
   - Clients les plus importants

4. **Rentabilité par type de bâtiment**
   - Profitabilité par segment

5. **Évolution trimestrielle du CA**
   - Tendances financières

6. **Analyse des délais de paiement**
   - Gestion des créances

7. **Top 10 bâtiments les plus rentables**
   - Meilleure performance financière

8. **Analyse par segment client**
   - Segmentation commerciale

### Data Mart 3: Impact Environnemental

**Fichier**: `03_queries_environnement.sql`

1. **Vue d'ensemble des émissions CO2**
   - Émissions par région

2. **Émissions mensuelles**
   - Évolution temporelle

3. **Top 10 bâtiments polluants**
   - Points d'amélioration prioritaires

4. **Émissions par type de bâtiment**
   - Impact par catégorie

5. **Taux de recyclage par région**
   - Performance environnementale

6. **Évolution trimestrielle**
   - Tendances des émissions

7. **Relation émissions/consommation**
   - Corrélations

8. **Impact de la certification énergétique**
   - Efficacité environnementale

### Requêtes Intégrées

**Fichier**: `04_queries_integrees.sql`

1. **Tableau de bord global par région**
   - Vue complète: consommation + rentabilité + environnement

2. **Performance globale par type de bâtiment**
   - Analyse multicritère

3. **Ratio rentabilité / impact environnemental**
   - Efficacité économique vs écologique

4. **Analyse saisonnière globale**
   - Patterns annuels

## 🎨 Suggestions de Visualisations

### 1. Tableau de Bord Principal

**Graphiques recommandés:**

- **KPIs** (Cartes):
  - Consommation totale (kWh)
  - CA TTC (€)
  - Émissions CO2 (tonnes)
  - Taux de recyclage moyen (%)

- **Graphique en barres**: Consommation par type d'énergie
- **Graphique linéaire**: Évolution mensuelle de la consommation
- **Carte**: Consommation par région (si données géographiques)
- **Graphique en camembert**: Répartition par type de bâtiment

### 2. Dashboard Consommation

- **Graphique en colonnes empilées**: Consommation par mois et type d'énergie
- **Graphique en barres horizontales**: Top 10 bâtiments consommateurs
- **Graphique linéaire**: Évolution trimestrielle
- **Heatmap**: Consommation par région × type d'énergie

### 3. Dashboard Rentabilité

- **Graphique en colonnes**: CA mensuel par région
- **Graphique en barres**: Top 10 clients
- **Graphique linéaire**: Évolution de la marge
- **Graphique en aires**: CA vs Coûts vs Marge
- **Graphique en barres**: Délais de paiement par tranche

### 4. Dashboard Environnemental

- **Graphique en colonnes**: Émissions CO2 par région
- **Graphique en barres horizontales**: Top 10 bâtiments polluants
- **Graphique en ligne**: Évolution des émissions
- **Graphique en bulles**: Émissions vs Taux de recyclage
- **Carte de chaleur**: Émissions par région × type de bâtiment

## 🛠️ Outils Recommandés

### Gratuits
- **MySQL Workbench**: Exécution et visualisation basique
- **Metabase**: Outil BI open-source
- **Grafana**: Dashboarding (requiert configuration)
- **Python + Pandas + Plotly**: Visualisations interactives

### Payants
- **Power BI**: Microsoft (licence étudiante gratuite)
- **Tableau**: Leader du marché
- **QlikView/QlikSense**: Visualisation avancée

## 📝 Prochaines Étapes

1. **Exécuter les requêtes** dans MySQL Workbench pour vérifier
2. **Choisir un outil de visualisation**
3. **Créer les tableaux de bord** selon les suggestions
4. **Personnaliser** selon vos besoins spécifiques
5. **Partager** les résultats avec les stakeholders

## 🔗 Connexion au Data Warehouse

**Configuration** (voir `config/database_config.ini`):
```
Host: localhost
Port: 3306
Database: greencity_dw
User: root
Password: [votre mot de passe]
```

## 📞 Support

Pour toute question ou problème, consultez:
- La documentation du schéma DW: `02_data_warehouse/schema/01_create_datawarehouse.sql`
- Les logs ETL: `logs/etl_YYYYMMDD.log`


