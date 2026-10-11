from inscription import register

def test_inscription():

    user_1 = register("KOUAGNI", "ANANGAMAN", "sedrick.kouagni@iit.ci", "0708432050", "SK Test")

    assert user_1.nom_complet() == "ANANGAMAN KOUAGNI"