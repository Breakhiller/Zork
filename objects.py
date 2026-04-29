class Piece:
    def __init__(self, nom, description):
        self.nom = nom
        self.description = description
        self.sorties = {}
        self.objets = []
        self.flags = {}

    def ajouter_sortie(self, direction, piece_destination):
        self.sorties[direction] = piece_destination

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def trouver_objet(self, nom):
        for objet in self.objets:
            if  objet.nom == nom:
                return objet
        return None

    def decrire(self):
        print()
        print(self.nom)
        print(self.description)

        if  self.objets:
            print("Objets visibles :",", ".join(objet.nom for objet in self.objets))

        if self.sorties:
            print("Sorties :", ", ".join(self.sorties.keys()))


class Objet:
    def __init__(self, nom, portable = True):
        self.nom = nom
        self.portable = portable
        self.etat = {}                  # allumé ou éteint

    def __repr__(self):
        return self.nom                 # évite d'avoir un nom eas56e11...

class Joueur:
    def __init__(self, position_depart):
        self.position = position_depart
        self.inventaire = []

    def trouver_objet(self, nom):
        for objet in self.inventaire:
            if  objet.nom == nom:
                return objet
        return None


class Engine:
    def __init__(self, piece_depart):
        self.joueur = Joueur(piece_depart)
        self.en_cours = True

    def lancer(self):
        print("Bienvenue")

        self.joueur.position.decrire()

        while self.en_cours:
            commande = input("\n ").strip().lower()
            self.traiter_commande(commande)

    def traiter_commande(self, commande):
        if  commande == "":
            return
        
        if  commande in ("quit", "exit"):
            self.en_cours = False
            print("Fin de la partie")
            return
        
        mots = commande.split()
        verbe = mots[0]
        complement = " ".join(mots[1:])

        if  verbe in ("prendre", "take"):
            self.prendre(complement)
        else:
            # pour nord, sud, est, ouest, entrer, sortir, monter, descendre ...        
            self.aller(commande)

    def aller(self, direction):
        # direction = self.direction
        piece = self.joueur.position

        if  direction in piece.sorties:
            self.joueur.position = piece.sorties[direction]
            self.joueur.position.decrire()
        else:
            print("Tu ne peux pas aller par là.")

    def prendre(self, nom_objet):
        if  nom_objet == "":
            print("Prendre quoi ?")

        piece = self.joueur.position
        objet = piece.trouver_objet(nom_objet)

        if  objet is None:
            print("Cet objet n'est pas ici")
            return
        
        if  not objet.portable:
            print("Tu ne peux pas rendre cet objet")
            return
        
        piece.objets.remove(objet)
        self.joueur.inventaire.append(objet)
        print(f"Tu prends {objet.nom}")


def creer_monde():
    devant_maison = Piece(
        "Devant la maison",
        "Tu es devant une petite maison blanche. Une porte mène vers l'intérieur."
    )
    salon = Piece(
        "Salon",
        "Tu es dans un vieux salon poussiéreux. Un tapis usé recouvre le sol."
    )

    cave = Piece(
        "Cave",
        "Tu es dans une cave sombre et humide. L'air sent la pierre froide."
    )

    foret = Piece(
        "Forêt",
        "Tu es dans une forêt calme. Les arbres entourent la maison"
    )

    # Sorties
    devant_maison.ajouter_sortie("entrer", salon)
    devant_maison.ajouter_sortie("nord", foret)

    salon.ajouter_sortie("sortir", devant_maison)
    salon.ajouter_sortie("descendre", cave)

    cave.ajouter_sortie("monter", salon)

    foret.ajouter_sortie("sud", devant_maison)

    # Objets
    lampe = Objet("lampe")
    corde = Objet("corde")
    boite = Objet("boîte aux lettres", portable=False)

    # Localisation objets
    devant_maison.ajouter_objet(boite)
    salon.ajouter_objet(lampe)
    cave.ajouter_objet(corde)

    # États locaux
    cave.flags["sombre"] = True
    salon.flags["tapis déplacé"] = False

    # Point d'entrée        
    return devant_maison    


# main
# if __name__ == "__main__" : 

piece_depart = creer_monde()
jeu = Engine(piece_depart)
jeu.lancer()