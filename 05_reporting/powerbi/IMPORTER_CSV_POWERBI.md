# 📥 Guide : Importer les CSV dans Power BI

Guide étape par étape pour importer les fichiers CSV exportés dans Power BI Desktop.

## 🚀 Méthode Rapide : Importer plusieurs CSV

### Étape 1 : Obtenir les fichiers CSV

Assurez-vous que les CSV sont exportés :
```bash
python 05_reporting\powerbi\export_tables_to_csv.py
```

Les fichiers seront dans : `D:\BI\05_reporting\powerbi\csv_export\`

### Étape 2 : Importer dans Power BI

1. **Ouvrir Power BI Desktop**

2. **Obtenir les données** → **Texte/CSV**

3. **Naviguer vers** : `D:\BI\05_reporting\powerbi\csv_export\`

4. **Sélectionner le premier fichier** (ex: `dim_date.csv`)

5. **Cliquer sur "Ouvrir"**

6. **Vérifier l'aperçu** :
   - Vérifier le délimiteur (normalement `,`)
   - Vérifier l'encodage (normalement UTF-8)
   - Cliquer sur **"Charger"** (ou **"Transformer les données"** pour nettoyer)

7. **Répéter pour chaque fichier** :
   - **Obtenir les données** → **Texte/CSV** → Sélectionner le fichier suivant
   - Ou utilisez la méthode "Dossier" ci-dessous

---

## 🚀 Méthode Avancée : Importer un Dossier

### Étape 1 : Importer depuis un dossier

1. **Obtenir les données** → **Dossier**

2. **Sélectionner le dossier** : `D:\BI\05_reporting\powerbi\csv_export\`

3. **Cliquer sur "Ouvrir"**

4. Dans la fenêtre qui s'ouvre :
   - Vous verrez tous les fichiers CSV listés
   - **Cliquer sur "Transformer les données"** en bas

### Étape 2 : Dans Power Query Editor

1. **Sélectionner un fichier** (ex: `dim_date.csv`)

2. **Cliquer sur "Modifier"** en bas

3. **Pour chaque fichier** :
   - Sélectionner le fichier
   - Cliquer sur **"Modifier"**
   - Vérifier les données
   - Renommer si nécessaire (ex: `dim_date` au lieu de `dim_date.csv`)
   - **Fermer et appliquer** (ou continuer pour le suivant)

4. **Une fois tous les fichiers vérifiés** :
   - **Fermer et appliquer**

---

## 📋 Liste des Fichiers à Importer

Importez ces fichiers dans cet ordre (dimensions d'abord, puis faits) :

### Dimensions :
- ✅ `dim_date.csv` - Dimension temporelle
- ✅ `dim_region.csv` - Régions
- ✅ `dim_batiment.csv` - Bâtiments
- ✅ `dim_client.csv` - Clients
- ✅ `dim_compteur.csv` - Compteurs
- ✅ `dim_type_energie.csv` - Types d'énergie

### Tables de Faits :
- ✅ `fact_consommation.csv` - Consommations
- ✅ `fact_rentabilite.csv` - Rentabilité
- ✅ `fact_environnement.csv` - Données environnementales

---

## 🔗 Étape 3 : Créer les Relations

Une fois les tables importées :

1. **Aller dans la Vue Modèle** (icône en bas à gauche)

2. **Vérifier les relations automatiques** :
   - Power BI peut détecter automatiquement certaines relations

3. **Créer les relations manquantes** :
   - Glisser `id_date` de `fact_consommation` vers `id_date` de `dim_date`
   - Glisser `id_region` de `fact_consommation` vers `id_region` de `dim_region`
   - etc.

4. **Vérifier les types de relations** :
   - Doivent être **Plusieurs à Un** (Many to One)
   - Cardinalité : Plusieurs vers Un
   - Filtre croisé : Les deux (Both)

---

## ✅ Vérification

### Vérifier que les données sont chargées :

1. **Vue Données** (icône en bas à gauche)

2. **Vérifier chaque table** :
   - Nombre de lignes
   - Colonnes présentes
   - Types de données

### Test rapide :

1. **Vue Rapport**

2. **Créer un graphique simple** :
   - Graphique en barres
   - Axe X : `nom_energie` (table `dim_type_energie`)
   - Valeur : `consommation_normalisee` (table `fact_consommation`) - Somme

Si le graphique s'affiche, tout fonctionne ! ✅

---

## 🔄 Mise à Jour des Données

Pour mettre à jour les données dans Power BI :

### Option 1 : Actualiser

1. **Accueil** → **Actualiser**

2. **D'abord, réexécutez le script d'export** :
   ```bash
   python 05_reporting\powerbi\export_tables_to_csv.py
   ```

3. **Puis actualiser** dans Power BI

### Option 2 : Actualiser automatique

Vous pouvez automatiser avec Power BI Service (si vous publiez sur le cloud), mais pour Desktop, c'est manuel.

---

## 💡 Astuces

### Renommer les tables

1. **Vue Données**
2. **Clic droit sur la table** → **Renommer**
3. Donner un nom clair (ex: "Consommation" au lieu de "fact_consommation")

### Nettoyer les données

1. **Clic droit sur la table** → **Modifier la requête**
2. Dans Power Query Editor :
   - Supprimer les colonnes inutiles
   - Changer les types de données
   - Renommer les colonnes

### Optimiser les performances

- Si les CSV sont très volumineux, utilisez des filtres dans Power Query
- Supprimez les colonnes non utilisées
- Créez des colonnes calculées plutôt que des mesures complexes

---

## 🎯 Prochaines Étapes

Une fois les données importées :

1. ✅ **Créer les relations** (Vue Modèle)
2. ✅ **Créer vos visualisations** (voir `DEMARRAGE_RAPIDE_POWERBI.md`)
3. ✅ **Créer des mesures DAX** (voir `GUIDE_POWER_BI.md`)

---

**Vous êtes prêt ! 🚀**


