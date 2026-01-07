# 🔧 Dépannage : Connexion MySQL dans Power BI

## ❌ Problème : "This connector requires one or more additional components"

Ce message apparaît car le connecteur MySQL natif de Power BI nécessite des composants supplémentaires.

---

## ✅ Solution 1 : Installer le Connecteur MySQL (Recommandé)

### Méthode A : Via le lien "Learn more"

1. **Cliquer sur "Learn more"** dans le dialogue Power BI
2. **Suivre les instructions** pour télécharger et installer :
   - **MySQL Connector/NET** ou
   - **MySQL ODBC Driver**

### Méthode B : Installation manuelle

#### Étape 1 : Télécharger MySQL Connector/NET

1. Aller sur : https://dev.mysql.com/downloads/connector/net/
2. Télécharger la dernière version (ex: `mysql-connector-net-8.x.x.msi`)
3. Installer le fichier `.msi`

#### Étape 2 : Redémarrer Power BI Desktop

1. **Fermer complètement** Power BI Desktop
2. **Rouvrir** Power BI Desktop
3. Réessayer la connexion MySQL

#### Étape 3 : Vérifier l'installation

1. Dans Power BI : **Obtenir les données** → **Base de données**
2. Vérifier que **"Base de données MySQL"** est disponible
3. Si c'est le cas, la connexion devrait fonctionner

---

## ✅ Solution 2 : Utiliser ODBC (Alternative)

Si le connecteur natif ne fonctionne pas, utilisez ODBC :

### Étape 1 : Installer MySQL ODBC Driver

1. Télécharger : https://dev.mysql.com/downloads/connector/odbc/
2. Installer : `mysql-connector-odbc-8.x.x-winx64.msi`
3. Choisir "Complete" lors de l'installation

### Étape 2 : Configurer la Source de Données ODBC

1. Ouvrir **"Sources de données ODBC"** (Windows)
   - Windows 10/11 : Rechercher "ODBC" dans le menu Démarrer
   - Ou : `Panneau de configuration` → `Outils d'administration` → `Sources de données ODBC`

2. **Onglet "DSN utilisateur"** → **Ajouter**

3. Sélectionner **"MySQL ODBC 8.x Unicode Driver"** → **Terminer**

4. **Configurer la connexion** :
   ```
   Data Source Name: GreenCity_DW
   TCP/IP Server: localhost
   Port: 3306
   User: root
   Password: [votre mot de passe]
   Database: greencity_dw
   ```

5. **Tester la connexion** → **OK**

### Étape 3 : Se connecter via Power BI

1. Dans Power BI : **Obtenir les données** → **Autres** → **ODBC**

2. Sélectionner **"GreenCity_DW"** (ou créer une nouvelle chaîne de connexion)

3. **OK** → Naviguer vers les tables

---

## ✅ Solution 3 : Exporter en CSV puis Importer (Temporaire)

Si les solutions ci-dessus ne fonctionnent pas, vous pouvez exporter les données en CSV :

### Créer un script d'export

J'ai créé un script Python qui exporte les tables principales en CSV.

**Voir** : `05_reporting/powerbi/export_tables_to_csv.py`

### Utiliser les CSV dans Power BI

1. **Obtenir les données** → **Texte/CSV**
2. Sélectionner les fichiers CSV exportés
3. **Charger** les données

⚠️ **Note** : Cette méthode est statique (pas de temps réel)

---

## ✅ Solution 4 : Utiliser DirectQuery via ODBC String

1. Dans Power BI : **Obtenir les données** → **Autres** → **ODBC**

2. **Chaîne de connexion** :
   ```
   Driver={MySQL ODBC 8.0 Unicode Driver};Server=localhost;Port=3306;Database=greencity_dw;User=root;Password=VOTRE_MOT_DE_PASSE;Option=3;
   ```
   ⚠️ Remplacez `VOTRE_MOT_DE_PASSE` par votre mot de passe MySQL

3. **OK** → Naviguer vers les tables

---

## 🎯 Solution Rapide Recommandée

**Pour aller vite** :

1. **Installer MySQL Connector/NET** (Solution 1 - Méthode B)
2. **Redémarrer Power BI**
3. **Réessayer la connexion**

Si ça ne fonctionne pas :
1. **Installer MySQL ODBC Driver** (Solution 2)
2. **Configurer ODBC**
3. **Se connecter via ODBC dans Power BI**

---

## 📋 Checklist de Dépannage

- [ ] MySQL est démarré et accessible sur `localhost:3306`
- [ ] Les identifiants sont corrects (voir `config/database_config.ini`)
- [ ] MySQL Connector/NET est installé
- [ ] Power BI Desktop a été redémarré après l'installation
- [ ] La base de données `greencity_dw` existe
- [ ] Les tables sont bien présentes dans la base

---

## 🔍 Vérifier la Connexion MySQL

Avant de continuer, testez la connexion MySQL :

```bash
# Dans PowerShell ou CMD
mysql -h localhost -u root -p greencity_dw
```

Si cette commande fonctionne, MySQL est accessible. Le problème est uniquement dans Power BI.

---

## 📞 Besoin d'Aide ?

Si aucune solution ne fonctionne :

1. Vérifiez la version de Power BI Desktop (doit être récente)
2. Vérifiez les logs Windows Event Viewer pour plus de détails
3. Essayez une version antérieure du connecteur MySQL
4. Utilisez la Solution 3 (CSV) comme solution temporaire

---

## 📚 Ressources

- **MySQL Connector/NET** : https://dev.mysql.com/downloads/connector/net/
- **MySQL ODBC Driver** : https://dev.mysql.com/downloads/connector/odbc/
- **Documentation Power BI MySQL** : https://docs.microsoft.com/power-bi/connect-data/desktop-connect-to-data


