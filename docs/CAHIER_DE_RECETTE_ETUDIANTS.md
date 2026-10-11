# Cahier de Recette Logicielle (Plan de Test)
## Projet : CantineMaster v1.0.0

> **Document :** Cahier de Recette & Cas de Tests (Test Cases Document)  
> **Auteur(s) :** [Noms des étudiants / Binôme]  
> **Date de recette :** [Date]  
> **Version testée :** 1.0.0 (Commit / Release de référence)  

---

## 1. Stratégie de Recette

### 1.1 Objectif
Vérifier la conformité de l'application **CantineMaster** par rapport aux spécifications fonctionnelles définies dans `SPECIFICATIONS_FONCTIONNELLES.md`.

### 1.2 Environnement de Test
- **Système d'exploitation :** macOS / Linux / Windows 11
- **Interpréteur :** Python 3.9+
- **Base de données :** SQLite (`cantine_dev.db` ou base en mémoire)
- **Navigateur Web :** Chrome / Firefox / Safari (dernières versions)
- **Jeu de données initial :** Chargé via la commande CLI `flask seed`

---

## 2. Matrice Synthétique de Traçabilité des Cas de Test

| Règle Exigence | Réf. Cas de Test | Intitulé du Test | Type de Test | Statut |
| :--- | :--- | :--- | :--- | :---: |
| `RG-USR-01` | `TC-SEC-001` | Tentative d'accès anonyme au tableau de bord | Sécurité | `PASS` |
| `RG-USR-02` | `TC-SEC-002` | Absence de lien d'inscription publique | Sécurité / IHM | `PASS` |
| `RG-USR-04` | `TC-USR-001` | Création utilisateur avec mot de passe trop court (< 8 car.) | Unitaire / Métier | `PASS` |
| `RG-USR-05` | `TC-SEC-003` | Restriction d'accès de l'Agent de Cantine au menu Utilisateurs | Sécurité / RBAC | `PASS` |
| `RG-USR-06` | `TC-USR-002` | Tentative de connexion avec un compte désactivé | Sécurité / Métier | `PASS` |
| `RG-ETU-01` | `TC-ETU-001` | Inscription d'un étudiant avec format matricule invalide | Fonctionnel / BVA | `PASS` |
| `RG-ETU-01` | `TC-ETU-002` | Inscription d'un étudiant avec matricule en doublon | Métier / BDD | `PASS` |
| `RG-ABO-01` | `TC-ABO-001` | Souscription avec date de fin antérieure à date de début | Métier / BVA | `PASS` |
| `RG-ABO-02` | `TC-ABO-002` | Détection de chevauchement sur deux abonnements actifs | Métier / Limite | `PASS` |
| `RG-ABO-04` | `TC-ABO-003` | Renouvellement automatique pour la période suivante | Fonctionnel | `PASS` |
| `RG-PAY-02` | `TC-PAY-001` | Encaissement d'un montant nul ou négatif (0.00 €) | Métier / BVA | `PASS` |
| `RG-PAY-03` | `TC-PAY-002` | Activation automatique d'abonnement après règlement du solde | Métier / Flux | `PASS` |
| `RG-FRQ-02` | `TC-FRQ-001` | Passage autorisé avec abonnement valide sur jour prévu | Fonctionnel | `PASS` |
| `RG-FRQ-02` | `TC-FRQ-002` | Rejet immédiat sur deuxième passage le même midi | Métier / Doublon | `PASS` |
| `RG-FRQ-03` | `TC-FRQ-003` | Rejet avec motif explicite sur abonnement suspendu pour impayé | Métier / Audit | `PASS` |
| `RG-FRQ-03` | `TC-FRQ-004` | Rejet avec motif explicite sur forfait 4 jours hors jour autorisé | Métier / Règles | `PASS` |

---

## 3. Fiches Détaillées des Cas de Tests

### Section A : Sécurité, Authentification & Rôles (RBAC)

#### `TC-SEC-001` : Tentative d'accès anonyme sans authentification
- **Exigence liée :** `RG-USR-01`
- **Priorité :** Bloquante
- **Préconditions :** Navigateur en mode navigation privée (aucun cookie de session actif).
- **Données de test :** URL directe `http://127.0.0.1:5000/`
- **Étapes d'exécution :**
  1. Ouvrir le navigateur.
  2. Saisir l'URL `http://127.0.0.1:5000/` dans la barre d'adresse et valider.
- **Résultat Attendu :**
  - Redirection automatique HTTP 302 vers `/login?next=%2F`.
  - Affichage de la page de connexion avec le message flash d'avertissement.
- **Résultat Obtenu :** Conforme. Redirection vers `/login`.
- **Statut :** `PASS`

---

#### `TC-SEC-003` : Contrôle RBAC - Accès restreint Agent de Pointage
- **Exigence liée :** `RG-USR-05`
- **Priorité :** Critique
- **Préconditions :** L'utilisateur `agent` est créé et actif (Rôle: `AGENT_POINTAGE`).
- **Données de test :** Identifiants `agent` / `Agent123!`, URL cible `/users/`
- **Étapes d'exécution :**
  1. Se connecter avec le compte `agent`.
  2. Vérifier que le menu "Utilisateurs" n'apparaît pas dans la barre de navigation.
  3. Saisir manuellement l'URL `http://127.0.0.1:5000/users/`.
- **Résultat Attendu :**
  - Le serveur refuse l'accès et renvoie une page d'erreur HTTP 403 Forbidden.
  - Aucune information confidentielle sur les utilisateurs n'est divulguée.
- **Résultat Obtenu :** Conforme. Page 403 affichée.
- **Statut :** `PASS`

---

### Section B : Inscription & Gestion des Étudiants

#### `TC-ETU-001` : Validation du format du matricule étudiant
- **Exigence liée :** `RG-ETU-01`
- **Priorité :** Majeure
- **Préconditions :** Connecté en tant que `gestionnaire` ou `admin`.
- **Données de test :** Matricule invalide = `ETU-99` (moins de 5 chiffres).
- **Étapes d'exécution :**
  1. Aller sur le menu *Étudiants* -> *Inscrire un Étudiant*.
  2. Saisir Matricule = `ETU-99`, Prénom = `Test`, Nom = `Erreur`, Email = `test@ecole.fr`, Classe = `Seconde`.
  3. Cliquer sur "Inscrire l'étudiant".
- **Résultat Attendu :**
  - L'étudiant n'est pas inséré en base de données.
  - Un message d'erreur rouge explicite s'affiche : *"Le matricule doit respecter le format 'ETU-XXXXX' (5 chiffres)"*.
- **Résultat Obtenu :** Conforme. Message d'erreur affiché, enregistrement bloqué.
- **Statut :** `PASS`

---

### Section C : Abonnements & Règlements

#### `TC-ABO-002` : Détection et blocage de chevauchement de dates
- **Exigence liée :** `RG-ABO-02`
- **Priorité :** Bloquante
- **Préconditions :** L'étudiant `ETU-10001` possède déjà un abonnement actif du 01/10 au 31/10.
- **Données de test :** Nouvelle souscription débutant le 15/10 et finissant le 15/11.
- **Étapes d'exécution :**
  1. Accéder au formulaire de nouvelle souscription pour `ETU-10001`.
  2. Choisir la formule "Plein Temps 5 Jours".
  3. Renseigner Début = `15/10/2026`, Fin = `15/11/2026`.
  4. Valider la souscription.
- **Résultat Attendu :**
  - Rejet de la demande par `SubscriptionService`.
  - Message flash rouge : *"Chevauchement interdit : l'étudiant possède déjà un abonnement actif ou en attente couvrant cette période"*.
- **Résultat Obtenu :** Conforme. Exception levée et message affiché.
- **Statut :** `PASS`

---

#### `TC-PAY-002` : Activation automatique après paiement intégral
- **Exigence liée :** `RG-PAY-03`
- **Priorité :** Critique
- **Préconditions :** Un abonnement existe au statut `EN_ATTENTE_PAIEMENT` d'un montant de 65.00 €.
- **Données de test :** Versement de 65.00 € par Carte Bancaire.
- **Étapes d'exécution :**
  1. Accéder au formulaire d'enregistrement de paiement.
  2. Sélectionner l'abonnement en attente.
  3. Saisir Montant = `65.00`, Mode = `Carte Bancaire`.
  4. Cliquer sur "Encaisser & Générer Quittance".
- **Résultat Attendu :**
  - Le paiement est créé avec référence unique `PAY-...` et quittance `REC-...`.
  - Le statut de l'abonnement bascule automatiquement à `ACTIF`.
  - Le solde restant dû passe à `0.00 €`.
- **Résultat Obtenu :** Conforme. L'abonnement est activé immédiatement.
- **Statut :** `PASS`

---

### Section D : Borne de Pointage Réfectoire

#### `TC-FRQ-001` : Contrôle d'accès - Passage normal autorisé
- **Exigence liée :** `RG-FRQ-02`
- **Priorité :** Bloquante
- **Préconditions :** L'étudiant `ETU-10001` a un abonnement 5j actif et n'a pas encore mangé aujourd'hui.
- **Données de test :** Matricule `ETU-10001`, service `DEJEUNER`.
- **Étapes d'exécution :**
  1. Se rendre sur la borne de pointage (`/attendance/`).
  2. Saisir `ETU-10001` et valider.
- **Résultat Attendu :**
  - Carte de résultat verte avec texte *"✅ ACCÈS AUTORISÉ"*.
  - Nom et classe de l'élève affichés.
  - Ajout immédiat d'une ligne dans le journal des passages du jour avec statut `AUTORISÉ`.
- **Résultat Obtenu :** Conforme. Feedback vert et son aigu validé.
- **Statut :** `PASS`

---

#### `TC-FRQ-002` : Contrôle d'accès - Rejet sur passage en double
- **Exigence liée :** `RG-FRQ-02`
- **Priorité :** Bloquante
- **Préconditions :** L'étudiant `ETU-10001` vient de valider son passage (`TC-FRQ-001`).
- **Données de test :** Même matricule `ETU-10001`, même service `DEJEUNER`.
- **Étapes d'exécution :**
  1. Immédiatement après le premier passage, ressaisir `ETU-10001`.
  2. Valider le passage.
- **Résultat Attendu :**
  - Carte de résultat rouge avec texte *"❌ ACCÈS REFUSÉ"*.
  - Motif explicite : *"Repas déjà consommé aujourd'hui"*.
  - Entrée horodatée ajoutée à l'historique avec statut `REFUSÉ` et motif `DEJA_CONSOMME`.
- **Résultat Obtenu :** Conforme. Rejet instantané avec motif précis.
- **Statut :** `PASS`

---

## 4. Modèle de Fiche d'Anomalie (Bug Report IEEE 829)

Si une anomalie est détectée au cours des tests, utilisez le modèle ci-dessous :

```markdown
### [BUG-001] Titre synthétique de l'anomalie

- **Composant concerné :** [ex: Borne Pointage / Caisse / Abonnements]
- **Sévérité :** [Bloquante / Critique / Majeure / Mineure]
- **Priorité de correction :** [Haute / Moyenne / Basse]
- **Auteur :** [Nom du testeur]
- **Date de détection :** [Date]

#### Description :
Description claire du problème rencontré.

#### Étapes de reproduction :
1. Se connecter avec l'utilisateur '...'
2. Naviguer vers '...'
3. Saisir '...' dans le champ '...'
4. Cliquer sur le bouton '...'

#### Résultat Observé :
Ce qui s'est réellement produit (ex: Erreur 500, crash, donnée incorrecte).

#### Résultat Attendu :
Ce qui aurait dû se produire conformément à la spécification (mentionner la règle RG concernée).

#### Données / Traces associées :
Extrait de logs ou capture d'écran de l'erreur.
```
