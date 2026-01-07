@echo off
REM ============================================================================
REM Script d'exécution de l'ETL GreenCity (Windows)
REM ============================================================================
REM Auteur: Équipe BI GreenCity
REM Date: Janvier 2026
REM Description: Script pour exécuter le processus ETL complet sur Windows
REM              À utiliser avec Task Scheduler
REM ============================================================================

SETLOCAL EnableDelayedExpansion

REM Configuration
SET PROJECT_HOME=C:\BI
SET PENTAHO_HOME=C:\pentaho\data-integration
SET LOG_DIR=%PROJECT_HOME%\logs
SET ETL_JOB=%PROJECT_HOME%\03_etl\pentaho\jobs\main_etl_job.kjb

REM Créer le répertoire de logs s'il n'existe pas
IF NOT EXIST "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Générer le nom du fichier log avec timestamp
FOR /f "tokens=2-4 delims=/ " %%a IN ('date /t') DO (SET mydate=%%c%%a%%b)
FOR /f "tokens=1-2 delims=/:" %%a IN ('time /t') DO (SET mytime=%%a%%b)
SET LOG_FILE=%LOG_DIR%\etl_%mydate%_%mytime%.log

REM Début de l'exécution
echo ========================================= >> "%LOG_FILE%"
echo Début de l'exécution de l'ETL GreenCity >> "%LOG_FILE%"
echo Date: %DATE% %TIME% >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"

REM Vérifier que Pentaho est installé
IF NOT EXIST "%PENTAHO_HOME%" (
    echo ERREUR: Pentaho Data Integration introuvable dans %PENTAHO_HOME% >> "%LOG_FILE%"
    exit /b 1
)

REM Vérifier que le job ETL existe
IF NOT EXIST "%ETL_JOB%" (
    echo ERREUR: Job ETL introuvable: %ETL_JOB% >> "%LOG_FILE%"
    exit /b 1
)

REM Exécuter le job Pentaho
echo Exécution du job ETL: %ETL_JOB% >> "%LOG_FILE%"
cd /d "%PENTAHO_HOME%"

call kitchen.bat ^
    /file:"%ETL_JOB%" ^
    /level:Basic ^
    /param:PROJECT_HOME="%PROJECT_HOME%" ^
    /param:EXECUTION_DATE=%mydate% ^
    >> "%LOG_FILE%" 2>&1

REM Vérifier le code de retour
IF %ERRORLEVEL% EQU 0 (
    echo ========================================= >> "%LOG_FILE%"
    echo ETL terminé avec SUCCÈS >> "%LOG_FILE%"
    echo ========================================= >> "%LOG_FILE%"
) ELSE (
    echo ========================================= >> "%LOG_FILE%"
    echo ETL terminé avec ERREUR (code: %ERRORLEVEL%^) >> "%LOG_FILE%"
    echo ========================================= >> "%LOG_FILE%"
)

REM Nettoyage des anciens logs (garder les 30 derniers jours)
forfiles /P "%LOG_DIR%" /M etl_*.log /D -30 /C "cmd /c del @path" 2>nul

echo Fin de l'exécution >> "%LOG_FILE%"
exit /b %ERRORLEVEL%

