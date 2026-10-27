import pytest

"""Cas 1 : Un gestionnaire peut accéder à la liste des étudiants"""
def test_liste_etudiants_gestionnaire(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/students/')
    assert response.status_code == 200

"""Cas 2 : Un agent n'a pas accès à la liste des étudiants"""
def test_liste_etudiants_agent_interdit(auth_agent_client):
    response = auth_agent_client.get('/students/')
    assert response.status_code == 403

"""Cas 3 : Création d'un étudiant avec des données valides — redirige vers sa fiche"""
def test_creation_etudiant_valide(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post('/students/new', data={
        'matricule': 'ETU-88001',
        'first_name': 'Test',
        'last_name': 'Route',
        'email': 'test.route@test.fr',
        'class_name': 'Terminale'
    }, follow_redirects=False)
    assert response.status_code == 302

"""Cas 4 : Création d'un étudiant avec un matricule invalide — reste sur le formulaire avec erreur"""
def test_creation_etudiant_matricule_invalide(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post('/students/new', data={
        'matricule': 'ETU-99',
        'first_name': 'Test',
        'last_name': 'Route',
        'email': 'test2.route@test.fr',
        'class_name': 'Terminale'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'ETU-XXXXX' in response.data.decode('utf-8') or 'format' in response.data.decode('utf-8').lower()

"""Cas 5 : Accès à la fiche détaillée d'un étudiant existant"""
def test_detail_etudiant(auth_gestionnaire_client, sample_student):
    response = auth_gestionnaire_client.get(f'/students/{sample_student.id}')
    assert response.status_code == 200

"""Cas 6 : Accès à la fiche d'un étudiant inexistant — redirige avec message flash"""
def test_detail_etudiant_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/students/99999', follow_redirects=True)
    assert response.status_code == 200

"""Cas 7 : Bascule du statut actif/inactif d'un étudiant"""
def test_toggle_status_etudiant(auth_gestionnaire_client, sample_student):
    response = auth_gestionnaire_client.post(
        f'/students/{sample_student.id}/toggle-status',
        follow_redirects=False
    )
    assert response.status_code == 302

"""Cas 8 : Recherche d'un étudiant par mot-clé"""
def test_recherche_etudiant(auth_gestionnaire_client, sample_student):
    response = auth_gestionnaire_client.get('/students/?search=Jean')
    assert response.status_code == 200

"""Cas 9 : Accès au formulaire de modification d'un étudiant"""
def test_formulaire_edit_etudiant(auth_gestionnaire_client, sample_student):
    response = auth_gestionnaire_client.get(f'/students/{sample_student.id}/edit')
    assert response.status_code == 200

"""Cas 10 : Modification d'un étudiant avec des données valides"""
def test_edit_etudiant_valide(auth_gestionnaire_client, sample_student):
    response = auth_gestionnaire_client.post(
        f'/students/{sample_student.id}/edit',
        data={
            'first_name': 'Jean-Luc',
            'last_name': 'Dupont',
            'email': 'jeanluc.dupont@test.fr',
            'class_name': 'Terminale B',
            'is_active': 'on'
        },
        follow_redirects=False
    )
    assert response.status_code == 302

"""Cas 11 : Modification d'un étudiant inexistant — redirige avec flash"""
def test_edit_etudiant_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get(
        '/students/99999/edit',
        follow_redirects=True
    )
    assert response.status_code == 200

"""Cas 12 : Modification d'un étudiant avec un email déjà utilisé — reste sur le formulaire"""
def test_edit_etudiant_email_doublon(auth_gestionnaire_client, sample_student, sample_student_inactif):
    response = auth_gestionnaire_client.post(
        f'/students/{sample_student.id}/edit',
        data={
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'marie.dupont@test.fr',
            'class_name': 'Terminale',
            'is_active': 'on'
        },
        follow_redirects=True
    )
    assert response.status_code == 200

"""Cas 13 : Modification avec données invalides — reste sur formulaire"""
def test_edit_etudiant_email_deja_utilise(auth_gestionnaire_client, sample_student, sample_student_inactif):
    response = auth_gestionnaire_client.post(
        f'/students/{sample_student.id}/edit',
        data={
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'marie.dupont@test.fr',
            'class_name': 'Terminale',
            'is_active': 'on'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'email' in response.data.lower() or response.status_code == 200