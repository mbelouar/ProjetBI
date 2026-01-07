# Configuration de Task Scheduler (Windows)

## Instructions pour automatiser l'ETL sur Windows

### Étape 1: Ouvrir Task Scheduler
1. Appuyer sur `Windows + R`
2. Taper `taskschd.msc` et appuyer sur Entrée
3. Le Planificateur de tâches s'ouvre

### Étape 2: Créer une nouvelle tâche
1. Dans le panneau de droite, cliquer sur **"Créer une tâche..."**
2. Ne pas utiliser "Créer une tâche de base" (moins d'options)

### Étape 3: Onglet Général
- **Nom**: `GreenCity_ETL_Daily`
- **Description**: `Exécution quotidienne de l'ETL GreenCity à 2h00`
- **Options de sécurité**:
  - ☑ Exécuter même si l'utilisateur n'est pas connecté
  - ☑ Exécuter avec les autorisations maximales
- **Configurer pour**: Windows 10 / Windows 11

### Étape 4: Onglet Déclencheurs
1. Cliquer sur **"Nouveau..."**
2. **Lancer la tâche**: Selon une planification
3. **Paramètres**:
   - ☑ Quotidien
   - **Démarrer le**: [Date actuelle]
   - **À**: 02:00:00
   - **Répéter tous les**: 1 jour
4. **Paramètres avancés**:
   - ☑ Activé
5. Cliquer sur **OK**

### Étape 5: Onglet Actions
1. Cliquer sur **"Nouveau..."**
2. **Action**: Démarrer un programme
3. **Programme/script**: 
   ```
   C:\BI\04_automation\scheduler\run_etl.bat
   ```
4. **Commencer dans (optionnel)**:
   ```
   C:\BI
   ```
5. Cliquer sur **OK**

### Étape 6: Onglet Conditions
- **Alimentation**:
  - ☐ Démarrer la tâche uniquement si l'ordinateur est relié au secteur
  - ☐ Arrêter si l'ordinateur bascule sur l'alimentation par batterie
- **Réseau**:
  - ☐ Démarrer uniquement si la connexion réseau suivante est disponible

### Étape 7: Onglet Paramètres
- ☑ Autoriser l'exécution de la tâche à la demande
- ☑ Exécuter la tâche dès que possible si un démarrage planifié est manqué
- ☐ Si la tâche échoue, recommencer tous les: [désactivé]
- **Si la tâche est déjà en cours d'exécution**:
  - ● Ne pas démarrer une nouvelle instance

### Étape 8: Finaliser
1. Cliquer sur **OK**
2. Entrer le mot de passe de l'utilisateur Windows si demandé
3. La tâche apparaît maintenant dans la liste

### Étape 9: Tester la tâche
1. Clic droit sur la tâche **GreenCity_ETL_Daily**
2. Cliquer sur **Exécuter**
3. Vérifier les logs dans `C:\BI\logs\`

## Commandes PowerShell utiles

### Lister les tâches planifiées
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "*GreenCity*"}
```

### Démarrer manuellement la tâche
```powershell
Start-ScheduledTask -TaskName "GreenCity_ETL_Daily"
```

### Arrêter la tâche en cours
```powershell
Stop-ScheduledTask -TaskName "GreenCity_ETL_Daily"
```

### Désactiver la tâche
```powershell
Disable-ScheduledTask -TaskName "GreenCity_ETL_Daily"
```

### Activer la tâche
```powershell
Enable-ScheduledTask -TaskName "GreenCity_ETL_Daily"
```

### Voir l'historique d'exécution
```powershell
Get-ScheduledTaskInfo -TaskName "GreenCity_ETL_Daily"
```

## Dépannage

### La tâche ne s'exécute pas
1. Vérifier que le chemin du script est correct
2. Vérifier que l'utilisateur a les droits d'exécution
3. Vérifier les logs dans le répertoire `logs/`
4. Consulter l'historique dans Task Scheduler:
   - Clic droit sur la tâche → Propriétés → Historique

### Erreur "Le système ne peut pas trouver le fichier spécifié"
- Vérifier que Pentaho est installé dans `C:\pentaho\data-integration`
- Vérifier que le projet est dans `C:\BI`
- Adapter les chemins dans `run_etl.bat` si nécessaire

### La tâche s'exécute mais échoue
- Ouvrir le fichier log le plus récent dans `C:\BI\logs\`
- Chercher les messages d'erreur
- Vérifier la connexion aux bases de données
- Vérifier que tous les fichiers sources sont présents

## Notifications par email (optionnel)

Pour recevoir des emails de notification:

1. Installer un client SMTP (ex: blat)
2. Modifier `run_etl.bat` pour ajouter l'envoi d'email
3. Exemple avec blat:
```batch
blat -to admin@greencity.com -subject "ETL Success" -body "ETL completed" -server smtp.gmail.com:587 -u your_email -pw your_password
```

## Monitoring

### Vérifier l'exécution quotidienne
- Consulter les logs dans `C:\BI\logs\`
- Vérifier la dernière exécution dans Task Scheduler
- Vérifier les données dans le Data Warehouse

### Alertes
- Configurer des alertes en cas d'échec
- Utiliser l'observateur d'événements Windows
- Mettre en place un monitoring externe (ex: Nagios, Zabbix)

