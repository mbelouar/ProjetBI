# 📊 Guide Power BI Desktop - GreenCity BI

Guide complet pour créer des dashboards dans Power BI Desktop avec vos données.

## 📋 Prérequis

1. **Power BI Desktop** installé (gratuit)
   - Téléchargement : https://powerbi.microsoft.com/desktop/
   - Licence étudiante : https://powerbi.microsoft.com/fr-fr/power-bi-pro/

2. **Connexion MySQL** fonctionnelle
   - MySQL doit être accessible sur `localhost:3306`
   - Identifiants dans `config/database_config.ini`

## 🚀 Étape 1 : Connexion au Data Warehouse

### Option A : Connexion Directe (Recommandée)

1. **Ouvrir Power BI Desktop**

2. **Obtenir les données** → **Base de données** → **Base de données MySQL**

3. **Paramètres de connexion** :
   ```
   Serveur: localhost
   Base de données: greencity_dw
   Mode de connectivité: DirectQuery (recommandé) ou Import
   ```

4. **Authentification** :
   - Mode : Utilisateur de base de données
   - Utilisateur : `root`
   - Mot de passe : (voir `config/database_config.ini`)

5. **Cliquer sur "Se connecter"**

### Option B : Importer via requêtes SQL (Plus de contrôle)

1. **Obtenir les données** → **Base de données** → **Base de données MySQL**

2. **Paramètres de connexion** (même que ci-dessus)

3. **Navigateur** → Cocher **"Activer la sélection de plusieurs éléments"**

4. **Sélectionner les tables nécessaires** :
   - ✅ `dim_date`
   - ✅ `dim_region`
   - ✅ `dim_batiment`
   - ✅ `dim_client`
   - ✅ `dim_compteur`
   - ✅ `dim_type_energie`
   - ✅ `fact_consommation`
   - ✅ `fact_rentabilite`
   - ✅ `fact_environnement`

5. **Cliquer sur "Charger"** (ou "Transformer les données" pour nettoyer avant)

## 🎨 Étape 2 : Créer vos premières visualisations

### Dashboard 1 : Consommation Énergétique

#### **Graphique 1 : Consommation par Type d'Énergie**

1. **Dans le volet Visualisations**, cliquer sur **Graphique en barres**

2. **Configurer les champs** :
   - Axe X : `dim_type_energie[nom_energie]`
   - Valeur : `fact_consommation[consommation_normalisee]` (Somme)

3. **Formater** :
   - Titre : "Consommation Totale par Type d'Énergie"
   - Couleurs : Personnaliser selon le type

#### **Graphique 2 : Top 10 Bâtiments Consommateurs**

1. **Graphique à barres horizontales**

2. **Configurer** :
   - Axe Y : `dim_batiment[nom_batiment]`
   - Valeur : `fact_consommation[consommation_normalisee]` (Somme)
   - Filtre : Top 10 par valeur

3. **Ajouter un filtre visuel** :
   - Glisser `dim_batiment[type_batiment]` dans Filtres visuels
   - Type : Liste déroulante

#### **Graphique 3 : Évolution Mensuelle**

1. **Graphique en courbes**

2. **Configurer** :
   - Axe X : `dim_date[periode_mois]`
   - Légende : `dim_type_energie[nom_energie]`
   - Valeur : `fact_consommation[consommation_normalisee]` (Somme)

3. **Filtre de date** :
   - Glisser `dim_date[annee]` dans Filtres visuels
   - Sélectionner 2024

### Dashboard 2 : Rentabilité Économique

#### **Graphique 1 : CA par Type d'Énergie**

1. **Graphique en colonnes empilées**

2. **Configurer** :
   - Axe X : `dim_type_energie[nom_energie]`
   - Valeur : 
     - `fact_rentabilite[montant_ttc]` (Somme)
     - `fact_rentabilite[cout_energie]` (Somme)
     - `fact_rentabilite[marge]` (Somme)

#### **Graphique 2 : Top 10 Clients**

1. **Graphique à barres horizontales**

2. **Configurer** :
   - Axe Y : `dim_client[raison_sociale]` ou `dim_client[nom]`
   - Valeur : `fact_rentabilite[montant_ttc]` (Somme)
   - Top 10

#### **Graphique 3 : Évolution Trimestrielle**

1. **Graphique en courbes**

2. **Configurer** :
   - Axe X : `dim_date[periode_trimestre]`
   - Valeur : `fact_rentabilite[montant_ttc]` (Somme)
   - Filtre : `dim_date[annee] = 2024`

### Dashboard 3 : Impact Environnemental

#### **Graphique 1 : Émissions CO2 par Région**

1. **Graphique en barres**

2. **Configurer** :
   - Axe X : `dim_region[nom_region]`
   - Valeur : `fact_environnement[emission_co2_kg]` (Somme)

3. **Convertir en tonnes** :
   - Créer une mesure : 
   ```
   Emissions CO2 (tonnes) = SUM(fact_environnement[emission_co2_kg]) / 1000
   ```

#### **Graphique 2 : Taux de Recyclage**

1. **Graphique en jauge (gauge)**

2. **Configurer** :
   - Valeur : `fact_environnement[taux_recyclage]` (Moyenne)
   - Minimum : 0
   - Maximum : 1

## 🔧 Étape 3 : Créer des Mesures (DAX)

### Mesures Recommandées

#### **Consommation Totale (kWh)**
```dax
Consommation Totale kWh = SUM(fact_consommation[consommation_normalisee])
```

#### **CA Total (€)**
```dax
CA Total = SUM(fact_rentabilite[montant_ttc])
```

#### **Marge Totale (€)**
```dax
Marge Totale = SUM(fact_rentabilite[marge])
```

#### **Taux de Marge (%)**
```dax
Taux de Marge = DIVIDE(
    SUM(fact_rentabilite[marge]),
    SUM(fact_rentabilite[montant_ttc]),
    0
) * 100
```

#### **Émissions CO2 (tonnes)**
```dax
Emissions CO2 Tonnes = SUM(fact_environnement[emission_co2_kg]) / 1000
```

#### **Consommation par m²**
```dax
Consommation par m² = 
DIVIDE(
    SUM(fact_consommation[consommation_normalisee]),
    SUM(dim_batiment[surface_m2]),
    0
)
```

#### **Taux de Recouvrement (%)**
```dax
Taux Recouvrement = 
DIVIDE(
    SUM(fact_rentabilite[montant_paye]),
    SUM(fact_rentabilite[montant_ttc]),
    0
) * 100
```

### Comment créer une mesure :

1. **Clic droit sur une table** (ex: `fact_consommation`)
2. **Nouvelle mesure**
3. **Copier-coller la formule DAX**
4. **Appuyer sur Entrée**

## 📊 Étape 4 : Relations entre Tables

Power BI devrait détecter automatiquement les relations, mais vérifiez :

1. **Vue Modèle** (icône en bas à gauche)
2. **Vérifier les relations** :
   - `fact_consommation[id_date]` → `dim_date[id_date]`
   - `fact_consommation[id_batiment]` → `dim_batiment[id_batiment]`
   - `fact_consommation[id_region]` → `dim_region[id_region]`
   - `fact_consommation[id_type_energie]` → `dim_type_energie[id_type_energie]`
   - etc.

3. **Créer des relations manuellement si nécessaire** :
   - Glisser-déposer entre les champs liés
   - Type : Plusieurs à Un (Many to One)

## 🎯 Étape 5 : Utiliser des Requêtes SQL Personnalisées

Au lieu d'importer toutes les tables, vous pouvez utiliser des requêtes SQL :

### Créer une requête SQL :

1. **Obtenir les données** → **Base de données** → **Base de données MySQL**

2. **Navigateur** → Cliquer sur **"Code avancé"**

3. **Coller une requête** depuis `05_reporting/sql/` :

```sql
SELECT 
    te.nom_energie,
    r.nom_region,
    SUM(fc.consommation_normalisee) AS consommation_totale
FROM fact_consommation fc
INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
INNER JOIN dim_region r ON fc.id_region = r.id_region AND r.est_actuel = TRUE
GROUP BY te.nom_energie, r.nom_region
```

4. **Nommer la requête** : "Consommation par Région et Type"

5. **Cliquer sur "OK"**

## 💡 Conseils Pro

### Performance

- **DirectQuery** : Pour données temps réel, mais peut être lent
- **Import** : Plus rapide, mais données statiques (rafraîchir manuellement)

### Filtres

- **Filtres de page** : Appliqués à toute la page
- **Filtres visuels** : Appliqués à un graphique spécifique
- **Filtres de rapport** : Appliqués à tout le rapport

### Formatage

1. **Sélectionner un graphique**
2. **Format** (icône pinceau)
3. **Personnaliser** : Couleurs, polices, titres, etc.

### Export

- **Fichier** → **Publier** → Publier sur Power BI Service (optionnel)
- **Fichier** → **Enregistrer** : Sauvegarde le fichier `.pbix`

## 📁 Structure Recommandée pour votre Rapport

```
Rapport Power BI
│
├── Page 1: Tableau de Bord Principal
│   ├── KPIs (4 cartes)
│   ├── Graphique consommation par type
│   ├── Graphique CA mensuel
│   └── Graphique émissions CO2
│
├── Page 2: Consommation Énergétique
│   ├── Filtres : Région, Type d'énergie, Période
│   ├── Top 10 bâtiments
│   ├── Évolution mensuelle
│   └── Répartition par zone climatique
│
├── Page 3: Rentabilité
│   ├── Filtres : Client, Région, Période
│   ├── Top 10 clients
│   ├── Évolution CA et marge
│   └── Analyse délais paiement
│
└── Page 4: Environnement
    ├── Filtres : Région, Type bâtiment
    ├── Émissions par région
    ├── Taux de recyclage
    └── Top bâtiments polluants
```

## 🔍 Dépannage

### Erreur de connexion MySQL
- Vérifier que MySQL est démarré
- Vérifier le port 3306
- Installer le connecteur MySQL si nécessaire

### Données lentes
- Utiliser **Import** au lieu de DirectQuery
- Ajouter des filtres pour limiter les données
- Optimiser les requêtes SQL

### Relations non détectées
- Créer manuellement dans la vue Modèle
- Vérifier les noms de colonnes (doivent correspondre)

## 📚 Ressources

- **Requêtes SQL** : `05_reporting/sql/`
- **Documentation Power BI** : https://docs.microsoft.com/power-bi/
- **Formation DAX** : https://www.sqlbi.com/guides/dax/

## ✅ Checklist

- [ ] Power BI Desktop installé
- [ ] Connexion au Data Warehouse établie
- [ ] Tables importées ou requêtes créées
- [ ] Relations vérifiées
- [ ] Mesures DAX créées
- [ ] Premières visualisations créées
- [ ] Rapport sauvegardé en `.pbix`

---

**Prêt à créer vos dashboards ! 🚀**


