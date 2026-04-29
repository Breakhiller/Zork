class Piece:
    def __init__(self, nom, description):
        self.nom = nom
        self.description = description
        self.sorties = {}

    def decrire(self):
        print()
        print(self.nom)
        print(self.description)

    def ajouter_sortie(self, direction, piece_destination):
        self.sorties[direction] = piece_destination

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
        piece = self.joueur.position
        objet = piece.tr



def creer_monde():
    devant_maison = Piece(
        "Devant la maison",
        "Tu es devant une petite maison blanche. Une porte mène vers l'intérieur."
    )
    salon = Piece(
        "Salon",
        "Tu es dans un vieux salon poussiéreux. Un tapis usé recouvre le sol."
    )

    foret = Piece(
        "Forêt",
        "Tu es dans une forêt calme. Les arbres entourent la maison"
    )

    # Sorties
    devant_maison.ajouter_sortie("entrer", salon)
    devant_maison.ajouter_sortie("nord", foret)

    salon.ajouter_sortie("sortir", devant_maison)

    foret.ajouter_sortie("sud", devant_maison)

    # Point d'entrée        
    return devant_maison    


# main

piece_depart = creer_monde()
jeu = Engine(piece_depart)
jeu.lancer()