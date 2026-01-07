# 🔧 Résolution : Erreur "Requested value 'None' was not found"

Cette erreur se produit généralement lors de la connexion MySQL dans Power BI. Voici plusieurs solutions.

## 🔍 Causes Possibles

1. Connecteur MySQL mal installé ou incompatible
2. Paramètres de connexion manquants
3. Version incompatible de Power BI
4. Problème avec les identifiants MySQL

---

## ✅ Solution 1 : Exporter en CSV (Plus Rapide et Fiable)

**Recommandation : Utiliser cette solution pour commencer rapidement !**

### Étape 1 : Exporter les tables

```bash
python 05_reporting\powerbi\export_tables_to_csv.py
```

Ce script va créer tous les CSV dans `05_reporting/powerbi/csv_export/`

### Étape 2 : Importer dans Power BI

1. Dans Power BI : **Obtenir les données** → **Texte/CSV**
2. Naviguer vers `D:\BI\05_reporting\powerbi\csv_export\`
3. Sélectionner les fichiers CSV :
   - `dim_date.csv`
   - `dim_region.csv`
   - `dim_batiment.csv`
   - `dim_client.csv`
   - `dim_compteur.csv`
   - `dim_type_energie.csv`
   - `fact_consommation.csv`
   - `fact_rentabilite.csv`
   - `fact_environnement.csv`

4. Pour chaque fichier :
   - Cliquer sur **"Charger"** (ou **"Transformer les données"** pour nettoyer)
   - Ou sélectionner plusieurs fichiers avec Ctrl+Clic

5. **C'est fait !** Vos données sont chargées.

⚠️ **Note** : Les données seront statiques. Pour mettre à jour, réexécutez le script et actualisez dans Power BI.

---

## ✅ Solution 2 : Vérifier la Connexion MySQL

Avant de continuer, vérifions que MySQL fonctionne :

### Test 1 : Connexion depuis la ligne de commande

```bash
mysql -h localhost -u root -p greencity_dw
```

Si ça fonctionne, MySQL est OK. Le problème vient de Power BI.

### Test 2 : Vérifier le port MySQL

```bash
# Vérifier que MySQL écoute sur le port 3306
netstat -an | findstr 3306
```

---

## ✅ Solution 3 : Utiliser ODBC avec Chaîne de Connexion Complète

### Étape 1 : Installer MySQL ODBC Driver

1. Télécharger : https://dev.mysql.com/downloads/connector/odbc/
2. Installer la version **8.x Unicode Driver**

### Étape 2 : Dans Power BI

1. **Obtenir les données** → **Autres** → **ODBC**

2. **Créer une nouvelle chaîne de connexion** :

   **Option A : Si ODBC est configuré**
   - Sélectionner votre DSN configuré

   **Option B : Chaîne de connexion directe**
   ```
   Driver={MySQL ODBC 8.0 Unicode Driver};Server=localhost;Port=3306;Database=greencity_dw;User=root;Password=VOTRE_MOT_DE_PASSE;Option=3;
   ```
   
   ⚠️ **Remplacez** `VOTRE_MOT_DE_PASSE` par votre mot de passe MySQL réel

3. **OK** → Naviguer vers les tables

---

## ✅ Solution 4 : Réinstaller le Connecteur MySQL

Si vous avez installé MySQL Connector/NET :

1. **Désinstaller** MySQL Connector/NET (Panneau de configuration → Programmes)

2. **Télécharger** la version la plus récente :
   - https://dev.mysql.com/downloads/connector/net/

3. **Installer** la version **.NET Framework** (pas .NET Core)

4. **Redémarrer** Power BI Desktop complètement

5. **Réessayer** la connexion

---

## ✅ Solution 5 : Utiliser une Requête SQL Directe

Au lieu de connecter à toute la base, connectez-vous avec une requête SQL spécifique :

1. **Obtenir les données** → **Base de données** → **Base de données MySQL**

2. **Paramètres** :
   - Serveur: `localhost`
   - Base de données: `greencity_dw`

3. **Navigateur** → Cliquer sur **"Code avancé"**

4. **Coller cette requête test** :
   ```sql
   SELECT 
       'Test' AS test_colonne,
       COUNT(*) AS nb_lignes
   FROM dim_date
   ```

5. **OK**

Si ça fonctionne, vous pouvez créer des requêtes personnalisées pour chaque visualisation.

---

## 🎯 Solution Recommandée : CSV + Power Query

### Avantages :
- ✅ Fonctionne toujours
- ✅ Pas de problème de connecteur
- ✅ Rapide à mettre en place
- ✅ Facile à maintenir

### Étapes :

1. **Exporter les données** :
   ```bash
   python 05_reporting\powerbi\export_tables_to_csv.py
   ```

2. **Créer un dossier de données** dans Power BI :
   - **Obtenir les données** → **Dossier**
   - Sélectionner `D:\BI\05_reporting\powerbi\csv_export\`
   - **Transformer les données**

3. **Dans Power Query Editor** :
   - Sélectionner tous les fichiers CSV
   - Cliquer sur **"Combiner et charger"** → **"Combiner et transformer"**
   - Power BI va automatiquement combiner les fichiers similaires

4. **Créer les relations** :
   - Aller dans la **Vue Modèle**
   - Créer les relations entre les tables (Power BI peut suggérer automatiquement)

5. **Créer vos visualisations** !

---

## 📋 Checklist de Dépannage

- [ ] MySQL est démarré et accessible
- [ ] Le port 3306 est ouvert
- [ ] Les identifiants sont corrects (voir `config/database_config.ini`)
- [ ] MySQL Connector/NET ou ODBC Driver est installé
- [ ] Power BI Desktop a été redémarré après installation
- [ ] La base de données `greencity_dw` existe bien
- [ ] Export CSV fonctionne (Solution 1)

---

## 🚀 Action Immédiate

**Pour continuer rapidement, utilisez la Solution 1 (CSV)** :

```bash
# 1. Exporter les données
python 05_reporting\powerbi\export_tables_to_csv.py

# 2. Dans Power BI :
#    - Obtenir les données → Texte/CSV
#    - Charger tous les CSV depuis csv_export/
```

C'est la méthode la plus fiable et rapide pour commencer !

---

## 💡 Pourquoi cette erreur ?

L'erreur "Requested value 'None' was not found" se produit souvent quand :
- Le connecteur MySQL essaie de lire un paramètre qui n'existe pas
- Il y a une incompatibilité entre les versions
- Les permissions MySQL ne sont pas correctes

La solution CSV contourne tous ces problèmes.

---

## 📞 Besoin d'Aide ?

Si aucune solution ne fonctionne :
1. Vérifiez les logs Windows Event Viewer
2. Essayez une version antérieure de Power BI Desktop
3. Utilisez la solution CSV qui fonctionne toujours


