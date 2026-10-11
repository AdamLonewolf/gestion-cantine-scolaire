# CantineMaster 🍽️
### Système de Gestion de Cantine Scolaire & Support de Cours "Test et Validation des Logiciels"

CantineMaster est une application web développée en **Python / Flask** pour la gestion intégrale de la restauration collective en milieu scolaire : inscriptions d'élèves, abonnements mensuels renouvelables, suivi des encaissements et contrôle d'accès en temps réel au réfectoire.

Ce projet a été spécialement conçu pour servir de **premier projet pratique pour des étudiants en Test et Validation des Logiciels (Assurance Qualité / QA Testing)**.

---

## 📚 Dossier Pédagogique (Livrables inclus)

L'ensemble de la documentation métier et pédagogique se trouve dans le dossier [`docs/`](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/) :

1. [**SPECIFICATIONS_FONCTIONNELLES.md**](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/SPECIFICATIONS_FONCTIONNELLES.md) | [Version PDF 📄](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/SPECIFICATIONS_FONCTIONNELLES.pdf) :  
   Cahier des charges exhaustif comprenant toutes les **Règles de Gestion numérotées** (`RG-USR`, `RG-ETU`, `RG-ABO`, `RG-PAY`, `RG-FRQ`), la matrice des rôles (RBAC), les diagrammes de cycle de vie et le dictionnaire de données.
2. [**SUJET_TP_TEST_VALIDATION.md**](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/SUJET_TP_TEST_VALIDATION.md) | [Version PDF 📄](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/SUJET_TP_TEST_VALIDATION.pdf) :  
   Énoncé complet du projet pour les étudiants (Mise en situation Ingénieur QA, 6 missions : Traçabilité, Partitions d'équivalence, Valeurs limites BVA, Table de décision, Automatisation Pytest, Fiches d'anomalies IEEE 829, et barème de notation sur 20 points).
3. [**CAHIER_DE_RECETTE_ETUDIANTS.md**](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/CAHIER_DE_RECETTE_ETUDIANTS.md) | [Version PDF 📄](file:///Users/sk/Documents/Test%20et%20val/Projet_1/docs/CAHIER_DE_RECETTE_ETUDIANTS.pdf) :  
   Modèle prêt à l'emploi de plan de test contenant une série de cas de test exemplaires (`TC-xxx`) pour guider les étudiants dans leur travail de recette.

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.9 ou version supérieure
- Gestionnaire de paquets `pip`

### 2. Installation de l'Environnement
```bash
# 1. Cloner ou se placer dans le répertoire du projet
cd "Projet_1"

# 2. Créer l'environnement virtuel
python3 -m venv .venv

# 3. Activer l'environnement virtuel
# Sur macOS / Linux :
source .venv/bin/activate
# Sur Windows (PowerShell) :
# .\.venv\Scripts\Activate.ps1

# 4. Installer les dépendances
pip install -r requirements.txt
```

### 3. Initialiser la Base de Données avec le Jeu d'Essai
Pour que les étudiants puissent immédiatement tester les règles métier, une commande d'amorçage injecte un jeu d'essai réaliste complet :
```bash
flask seed
```

### 4. Lancer l'Application
```bash
python run.py
```
Accédez ensuite à l'application dans votre navigateur : **`http://127.0.0.1:5000/`**

---

## 👥 Comptes Utilisateurs Pré-configurés

Conformément à la règle `RG-USR-02`, **il n'y a pas d'inscription libre publique**.  
L'accès s'effectue via des comptes habilités créés par l'administrateur :

| Identifiant | Mot de passe | Rôle | Périmètre d'Accès |
| :--- | :--- | :--- | :--- |
| **`admin`** | `Admin123!` | `ADMIN` | Accès total + Gestion des utilisateurs internes |
| **`gestionnaire`**| `Gest123!` | `GESTIONNAIRE` | Gestion des étudiants, abonnements et encaissements |
| **`agent`** | `Agent123!` | `AGENT_POINTAGE`| Accès réservé à la borne de pointage cantine |

---

## 🧪 Profils d'Étudiants pour les Tests (Jeu d'essai)

La commande `flask seed` crée automatiquement 6 profils d'étudiants illustrant des cas de test clés :

- **`ETU-10001` (Lucas Martin)** : Abonnement 5 jours **ACTIF & RÉGLÉ** $\rightarrow$ *Passage autorisé à la cantine*.
- **`ETU-10002` (Camille Dubois)** : Forfait **Demi-Pension 4 jours** (Lun, Mar, Jeu, Ven) $\rightarrow$ *Refus le mercredi (`JOUR_NON_AUTORISE`)*.
- **`ETU-10003` (Youssef Benali)** : Abonnement **EXPIRÉ** le mois dernier $\rightarrow$ *Refus (`ABONNEMENT_EXPIRE`)*.
- **`ETU-10004` (Emma Leroy)** : Abonnement **SUSPENDU POUR IMPAYÉ** $\rightarrow$ *Refus (`IMPAYE_SUSPENDU`)*.
- **`ETU-10005` (Thomas Moreau)** : Inscrit mais **SANS AUCUN ABONNEMENT** $\rightarrow$ *Refus (`PAS_D_ABONNEMENT`)*.
- **`ETU-10006` (Chloé Roux)** : Dossier étudiant **INACTIF** $\rightarrow$ *Refus (`ETUDIANT_INACTIF`)*.

---

## ⚡ Exécution des Tests Automatisés (Pytest)

Le projet intègre une suite de tests automatisés de référence validant les règles de gestion et servant de corrigé modèle pour l'enseignant :

```bash
# Exécution de l'ensemble des tests
pytest -v

# Exécution avec rapport de couverture de code
pytest --cov=app tests/

# Exécution ciblée sur un module spécifique
pytest tests/test_boundary_cases.py -v
pytest tests/test_services/test_attendance_service.py -v
pytest tests/test_routes/test_security_rbac.py -v
```

---

## 📁 Architecture du Code Source

```
Projet_1/
├── app/
│   ├── models/                 # Modèles SQLAlchemy (User, Student, Plan, Subscription, Payment, AttendanceLog)
│   ├── services/               # Logique métier pure découplée (AuthService, StudentService, AttendanceService...)
│   ├── routes/                 # Contrôleurs Flask et contrôle d'accès RBAC
│   ├── templates/              # Vues HTML5 Jinja2 avec design moderne et responsive
│   ├── static/                 # Styles CSS et scripts interactifs (feedback borne)
│   └── cli.py                  # Commandes CLI (flask init-db, flask seed)
├── config.py                   # Configurations Dev, Testing, Prod
├── run.py                      # Point d'entrée de l'application
├── requirements.txt            # Dépendances du projet
├── pytest.ini                  # Configuration Pytest
├── tests/                      # Suite de tests unitaires, d'intégration et limites
│   ├── conftest.py             # Fixtures Pytest partagées
│   ├── test_boundary_cases.py  # Analyse des valeurs limites (BVA)
│   ├── test_routes/            # Tests des routes et de la sécurité RBAC
│   └── test_services/          # Tests unitaires des services métier
└── docs/                       # Livrables pédagogiques complets
    ├── SPECIFICATIONS_FONCTIONNELLES.md
    ├── SUJET_TP_TEST_VALIDATION.md
    └── CAHIER_DE_RECETTE_ETUDIANTS.md
```
