class Account():

    def __init__(self, nom, prenoms, email, contact, bio):

        self.nom = nom
        self.prenoms = prenoms
        self.email = email
        self.contact = contact
        self.bio = bio

    def nom_complet(self):
        return f"{self.nom} {self.prenoms}"



def register(nom, prenoms, email, contact, bio):
    account = Account(nom=nom, prenoms=prenoms, email=email, contact=contact, bio=bio)
    return account

