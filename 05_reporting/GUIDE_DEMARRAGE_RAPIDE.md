# 🚀 Guide de Démarrage Rapide - Reporting BI

Ce guide vous montre **comment commencer** avec les rapports BI pour votre projet GreenCity.

## ✅ Ce qui a été créé

### 1. **Requêtes SQL** (`05_reporting/sql/`)
- ✅ `01_queries_consommation.sql` - 8 requêtes pour le Data Mart Consommation
- ✅ `02_queries_rentabilite.sql` - 8 requêtes pour le Data Mart Rentabilité
- ✅ `03_queries_environnement.sql` - 8 requêtes pour le Data Mart Environnement
- ✅ `04_queries_integrees.sql` - 4 requêtes intégrées (vue globale)

### 2. **Scripts Python** (`05_reporting/python/`)
- ✅ `test_queries.py` - Teste et affiche les résultats des requêtes
- ✅ `visualizations.py` - Génère 6 graphiques automatiquement

### 3. **Visualisations générées** (`05_reporting/visualizations/`)
- ✅ 6 graphiques PNG prêts à utiliser

## 📝 Étape par étape

### **ÉTAPE 1 : Tester les requêtes SQL**

```bash
# Tester les requêtes principales
python 05_reporting\python\test_queries.py
```

**Ce que vous verrez :**
- Résultats des requêtes principales
- Aperçu des données du Data Warehouse
- Validation que tout fonctionne

### **ÉTAPE 2 : Générer les graphiques**

```bash
# Générer tous les graphiques
python 05_reporting\python\visualizations.py
```

**Graphiques créés :**
1. `01_consommation_par_type.png` - Barres : consommation par type d'énergie
2. `02_top_batiments_consommateurs.png` - Barres horizontales : top 10 bâtiments
3. `03_evolution_mensuelle.png` - Lignes : évolution mensuelle 2024
4. `04_rentabilite_par_type.png` - Barres groupées : CA, coûts, marge
5. `05_emissions_co2_par_region.png` - Barres : émissions par région
6. `06_tableau_bord_kpis.png` - 4 cartes KPI principales

### **ÉTAPE 3 : Utiliser les requêtes dans MySQL Workbench**

1. **Ouvrir MySQL Workbench**
2. **Se connecter** au Data Warehouse :
   - Host: `localhost`
   - Port: `3306`
   - Database: `greencity_dw`
   - User: `root`
   - Password: (voir `config/database_config.ini`)

3. **Exécuter une requête** :
   ```sql
   USE greencity_dw;
   
   -- Copier-coller une requête depuis 05_reporting/sql/01_queries_consommation.sql
   SELECT 
       te.nom_energie AS 'Type Énergie',
       ROUND(SUM(fc.consommation_normalisee), 2) AS 'Consommation Totale (kWh)'
   FROM fact_consommation fc
   INNER JOIN dim_type_energie te ON fc.id_type_energie = te.id_type_energie
   GROUP BY te.nom_energie;
   ```

### **ÉTAPE 4 : Créer vos propres visualisations**

#### Option A : Avec Python (recommandé pour débuter)

Modifiez `05_reporting/python/visualizations.py` :

```python
def ma_nouvelle_visualisation(output_dir, conn):
    """Mon nouveau graphique"""
    query = """
    SELECT 
        r.nom_region,
        SUM(fc.consommation_normalisee) AS consommation
    FROM fact_consommation fc
    INNER JOIN dim_region r ON fc.id_region = r.id_region
    GROUP BY r.nom_region
    """
    
    df = pd.read_sql(query, conn)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df['nom_region'], df['consommation'])
    ax.set_title('Ma Visualisation')
    save_figure(fig, 'ma_visualisation.png', output_dir)
```

Puis ajoutez l'appel dans `main()` :
```python
ma_nouvelle_visualisation(output_dir, conn)
```

#### Option B : Avec Power BI / Tableau

1. **Se connecter au Data Warehouse MySQL**
2. **Importer une requête SQL** depuis `05_reporting/sql/`
3. **Créer des visualisations** avec l'interface graphique

#### Option C : Avec Metabase (gratuit et simple)

1. **Installer Metabase** : https://www.metabase.com/
2. **Ajouter la connexion MySQL** au Data Warehouse
3. **Créer des questions** (requêtes SQL ou interface graphique)
4. **Créer des tableaux de bord**

## 🎯 Requêtes Recommandées pour Commencer

### Pour un Dashboard Consommation :
```sql
-- 1. Vue d'ensemble par type d'énergie (Requête #1)
-- 2. Top 10 bâtiments consommateurs (Requête #3)
-- 3. Évolution mensuelle (Requête #5)
-- 4. Consommation par région (Requête #2)
```

### Pour un Dashboard Rentabilité :
```sql
-- 1. Vue d'ensemble rentabilité (Requête #1)
-- 2. Top 10 clients (Requête #3)
-- 3. Évolution trimestrielle CA (Requête #5)
-- 4. Analyse délais paiement (Requête #6)
```

### Pour un Dashboard Environnement :
```sql
-- 1. Émissions par région (Requête #1)
-- 2. Top 10 bâtiments polluants (Requête #3)
-- 3. Évolution mensuelle émissions (Requête #2)
-- 4. Taux de recyclage (Requête #5)
```

## 📊 Structure des Requêtes

Chaque fichier SQL contient :
- **8 requêtes** pour chaque Data Mart
- **Commentaires** expliquant chaque requête
- **Ordre logique** : du général au détaillé
- **Prêt à l'emploi** : copier-coller et exécuter

## 🛠️ Dépendances Python

Si vous n'avez pas les bibliothèques nécessaires :

```bash
pip install pandas matplotlib seaborn mysql-connector-python
```

## 📁 Fichiers Générés

Après exécution de `visualizations.py`, vous trouverez dans `05_reporting/visualizations/` :

```
05_reporting/visualizations/
├── 01_consommation_par_type.png
├── 02_top_batiments_consommateurs.png
├── 03_evolution_mensuelle.png
├── 04_rentabilite_par_type.png
├── 05_emissions_co2_par_region.png
└── 06_tableau_bord_kpis.png
```

## 💡 Conseils

1. **Commencez simple** : Testez d'abord avec `test_queries.py`
2. **Explorez les données** : Modifiez les requêtes pour voir différents angles
3. **Personnalisez** : Adaptez les graphiques à vos besoins
4. **Documentez** : Notez les insights trouvés

## 🔍 Dépannage

### Erreur de connexion MySQL
- Vérifiez que MySQL est démarré
- Vérifiez les identifiants dans `config/database_config.ini`
- Testez la connexion : `mysql -u root -p greencity_dw`

### Graphiques non générés
- Installez matplotlib : `pip install matplotlib`
- Vérifiez les permissions d'écriture dans `05_reporting/visualizations/`

### Requêtes lentes
- Vérifiez les index dans le Data Warehouse
- Limitez les résultats avec `LIMIT 100`
- Filtrez par date : `WHERE dd.annee = 2024`

## 🎓 Prochaines Étapes

1. ✅ **Tester les requêtes** → `python 05_reporting\python\test_queries.py`
2. ✅ **Générer les graphiques** → `python 05_reporting\python\visualizations.py`
3. ✅ **Explorer les données** → Modifier les requêtes SQL
4. ✅ **Créer des dashboards** → Utiliser Power BI, Tableau, ou Metabase
5. ✅ **Documenter vos insights** → Noter les découvertes importantes

## 📞 Besoin d'aide ?

- Consultez `README_REPORTING.md` pour plus de détails
- Vérifiez les logs ETL : `logs/etl_YYYYMMDD.log`
- Examinez le schéma DW : `02_data_warehouse/schema/01_create_datawarehouse.sql`

---

**Bonne analyse ! 🚀**


