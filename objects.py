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

#        if  self.objets:
#            print("Objets visibles :",", ".join(objet.nom for objet in self.objets))

        if  self.objets:
            for objet in self.objets:
                print(f"Il y a {objet.description} ici")

        if self.sorties:
            print("Sorties :", ", ".join(self.sorties.keys()))


class Objet:
    def __init__(self, nom, description, portable = True):
        self.nom = nom
        self.description = description
        self.portable = portable
        self.props = {}                 # ce que l'objet peut faire
        self.etat = {}                  # allumé ou éteint
        self.actions = {}   

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
    def __init__(self, monde):
        self.monde = monde
        self.joueur = Joueur(monde["depart"])
        self.en_cours = True

    def lancer(self):
        print("Bienvenue")

#        self.joueur.position.decrire()
        self.decrire_position()

        while self.en_cours:
            commande = input("\n ").strip().lower()
            self.traiter_commande(commande)

    def trouver_objet_global(self, nom_objet):
        piece = self.joueur.position

        objet = piece.trouver_objet(nom_objet)
        if  objet:
            return objet, "piece"
        
        objet = self.joueur.trouver_objet(nom_objet)
        if  objet:
            return objet, "inventaire"
        
        return None, None

    def traiter_commande(self, commande):
        if  commande == "":
            return
        
        if  commande in ("quit", "exit"):
            self.en_cours = False
            print("Fin de la partie")
            return
        
        if  commande in("regarder", "look"):
            self.decrire_position()
            return
        
        mots = commande.split()
        verbe = mots[0]
        complement = " ".join(mots[1:])

        if  verbe in ("prendre", "take"):
            self.prendre(complement)
        elif verbe in ("déplacer", "soulever"):
            self.executer_action_objet("deplacer", complement)
        elif verbe == "allumer":
            self.allumer(complement)
        elif verbe == "examiner":
            self.examiner(complement)
        elif verbe == "ouvrir":
            self.executer_action_objet("ouvrir", complement)
        elif verbe == "poser":
            self.poser(complement)
        else:
            # pour nord, sud, est, ouest, entrer, sortir, monter, descendre ...        
            self.aller(commande)

    def aller(self, direction):
        # direction = self.direction
        piece = self.joueur.position

        if  direction in piece.sorties:
            self.joueur.position = piece.sorties[direction]
#            self.joueur.position.decrire()
            self.decrire_position()
        else:
            print("Tu ne peux pas aller par là.")

    def allumer(self, nom_objet):
        objet = self.joueur.trouver_objet(nom_objet)

        if  objet is None:
            print("Tu n'as pas cet objet")
            return

        if not objet.props.get("allumable"):
            print("Tu ne peux pas allumer ça.")
            return  
        
        objet.etat["allumee"] = True
        print(f"La {objet.nom} est maintenant allumée")

    def examiner(self, nom_objet):
        if  nom_objet == "":
            print("examiner quoi ?")
            return
        
        objet, origine = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Tu ne vois pas cet objet ici.")
            return
        
        if  origine == "piece":
            print("Tu regardes autour de toi...")
        else:
            print("Tu regardes dans ton inventaire...")
        
        print(objet.description)

    def prendre(self, nom_objet):
        if  nom_objet == "":
            print("Prendre quoi ?")
            return

        objet, origine = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Cet objet n'est pas ici")
            return
        
        if  origine == "inventaire":
            print("Tu l'as déjà")
            return
        
        if  not objet.portable:
            print("Tu ne peux pas prendre cet objet")
            return
        
        piece = self.joueur.position
        piece.objets.remove(objet)
        self.joueur.inventaire.append(objet)
        print(f"Tu prends {objet.nom}")

    def poser(self, nom_objet):
        if  nom_objet == "":
            print("poser quoi ?")
            return
        
        objet, origine = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Tu n'as pas cet objet")
            return

        if  origine == "piece":
            print("Cet objet est déjà ici.")
            return
        
        self.joueur.inventaire.remove(objet)
        piece = self.joueur.position
        piece.objets.append(objet)
        print(f"Tu poses {objet.nom}")


    def decrire_position(self):
        piece:Piece = self.joueur.position

        if  piece.flags.get("sombre", False) and not self.joueur_a_lumiere():
            print("Il fait trop sombre pour voir quoi que ce soit")
            return
        
        piece.decrire()

    def joueur_a_lumiere(self):
        # lumière portée dans l'inventaire
        for objet in self.joueur.inventaire:
            if  objet.props.get("lumiere", False) and objet.etat.get("allumee", False):
                return True
            
        # lumière dans la pièce
        for objet in self.joueur.position.objets:
            if  objet.props.get("lumiere", False) and objet.etat.get("allumee", False):
                return True

        return False
    
    def executer_action_objet(self, action, nom_objet):
        piece:Piece = self.joueur.position
        objet:Objet = piece.trouver_objet(nom_objet)              # cherche objet dans Piece
#        print(piece.nom)
#        print(objet)

        if  objet is None:                                  # rien trouvé dans la pièce
            objet = self.joueur.trouver_objet(nom_objet)    # cherche objet dans l'inventaire

        if  objet is None:                                  # rien trouvé dans l'inventaire
            print("Tu ne vois pas cet objet ici")
            return
        
        # objet trouvé, on fait quoi avec (si on peut, dépend si action définie dans objet)
        if  action not in objet.actions:
            print("Rien d'intéressant ne se produit.")
            return
        
        regle = objet.actions[action]
        conditions = regle.get("conditions", {})

        # le cas échéant, les conditions de l'action sont-elles remplies
        for flag, valeur_attendue in conditions.get("flags", {}).items():
            if  piece.flags.get(flag, False) != valeur_attendue:
                print("Tu ne peux pas faire ça pour le moment")
                return

        # Modifier les flags de la pièce actuelle
        for flag, valeur in regle.get("set_flags", {}).items():
            piece.flags[flag] = valeur

        # Révéler des sorties
        for direction, id_piece in regle.get("revele_sorties", {}).items():
            piece.ajouter_sortie(direction, self.monde[id_piece])
            self.monde[id_piece].ajouter_sortie("monter", piece)

        print(regle.get("message", "Action effectuée."))



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
#    salon.ajouter_sortie("descendre", cave)

    cave.ajouter_sortie("monter", salon)

    foret.ajouter_sortie("sud", devant_maison)

    # Monde
    monde = {
        "depart": devant_maison,
        "salon": salon,
        "cave": cave,
        "foret": foret
    }

    # Objets
    lampe = Objet("lampe", "Une vieille lampe possiéreuse")
    lampe.props = {"lumiere": True, "allumable": True}
    lampe.etat["allumee"] = False
    tapis = Objet("tapis", "Un grand tapis d'orient au centre de la pièce")
    tapis.props = {"deplacable": True}
    tapis.actions["deplacer"] = {
        "message": "Tu déplaces le tapis. Une trappe apparaît sur le sol",
        "set_flags": {"tapis_deplace": True, "trappe_visible": True}
#        "revele_sorties": {"descendre": "cave"}
    }
    corde = Objet("corde", "Une corde usée, mais solide")
    boite = Objet("boîte aux lettres", "Une boîte aux lettres ouverte", portable=False)
    trappe = Objet("trappe", "Une trappe en bois, partiellement cachée sous le tapis apparaît sur le sol", portable=False)
    trappe.actions["ouvrir"] = {
        "message": "Tu ouvres la trappe. Un escalier descend dans l'obscurité",
        "conditions": {"flags": {"trappe_visible": True}},
        "set_flags": {"trappe_ouverte": True},
        "revele_sorties": {"descendre": "cave"}
    }

    # Localisation objets
    devant_maison.ajouter_objet(boite)
    salon.ajouter_objet(lampe)
    salon.ajouter_objet(tapis)
    salon.ajouter_objet(trappe)
    cave.ajouter_objet(corde)

    # États locaux (pièces)
    cave.flags["sombre"] = True
    salon.flags["tapis déplacé"] = False
    salon.flags["trappe visible"] = False
    salon.flags["trappe ouverte"] = False


    # Point d'entrée        
    return monde    


# main
if __name__ == "__main__" :
    monde = creer_monde()
    jeu = Engine(monde)
    jeu.lancer()