import random   # après split en plusieurs fichiers,mettre dans Engine.py

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
                if  objet.props.get("visible", True):
                        print(f"Il y a {objet.description} ici")

                        if  objet.props.get("support", False) and objet.objets_sur:
                            print(f"Sur {objet.nom}, tu vois :")
                            for obj in objet.objets_sur:
                                print(f"- {obj.description}")

                        if  objet.props.get("conteneur", False):
                            if  objet.props.get("ouvrable", False) and not objet.etat.get("ouvert", False):
                                pass
                            else:
                                if  objet.contenu:
                                    print(f"Dans {objet.nom}, tu vois :")
                                    for obj in objet.contenu:
                                        print(f"- {obj.description}")

#        if self.sorties:
#            print("Sorties :", ", ".join(self.sorties.keys()))


class Objet:
    def __init__(self, nom, description, portable = True):
        self.nom = nom
        self.description = description
        self.portable = portable
        self.props = {}                 # ce que l'objet peut faire
        self.etat = {}                  # allumé ou éteint
        self.actions = {}
        self.contenu = []
        self.objets_sur = [] 

    def __repr__(self):
        return self.nom                 # évite d'avoir un nom eas56e11...
    
    def chercher_dans_liste(self, liste, nom):
        for objet in liste:
            if  objet.nom == nom and objet.props.get("visible", True):
                return objet
        return None
    
#    def trouver_objet(self, nom):
#        for objet in self.contenu:
#            if  objet.nom == nom and objet.props.get("visible", True):
#                return objet
#        return None

    def trouver_objet(self, nom):
        return self.chercher_dans_liste(self.objets, nom)

    def trouver_objet_dans(self, nom):
        return self.chercher_dans_liste(self.contenu, nom)

    def trouver_objet_sur(self, nom):
        return self.chercher_dans_liste(self.objets_sur, nom)


class Joueur:
    def __init__(self, position_depart):
        self.position = position_depart
        self.inventaire = []

    def trouver_objet(self, nom):
        for objet in self.inventaire:
            if  objet.nom == nom and objet.props.get("visible", True):
                return objet
        return None


class Engine:
    def __init__(self, monde):
        self.monde = monde
        self.joueur = Joueur(monde["depart"])
        self.en_cours = True
        self.tours_dans_le_noir = 0

# -------------------------------------------------------
#               Coeur du moteur
# -------------------------------------------------------

    def lancer(self):
        print("Bienvenue")
        self.decrire_position()

        while self.en_cours:
            commande = input("\n>").strip().lower()
            self.traiter_commande(commande)

            if  self.en_cours:
                self.decrementer_lampe()
                self.gerer_obscurite()

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
        
        # traitement mettre ou poser un objet dans ou sur un conteneur
        if  commande.startswith("mettre ") and " dans " in commande:
            reste = commande.replace("mettre ", "" , 1)
            nom_objet, nom_conteneur = reste.split(" dans ", 1)
            self.mettre_dans(nom_objet, nom_conteneur)
            return
        
        if  commande.startswith("poser ") and " sur " in commande:
            reste = commande.replace("poser ", "" , 1)
            nom_objet, nom_support = reste.split(" sur ", 1)
            self.poser_sur(nom_objet, nom_support)
            return
        
        # cas normaux verbe complément
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
            self.ouvrir(complement)
        elif verbe == "poser":
            self.poser(complement)
        else:
            # pour nord, sud, est, ouest, entrer, sortir, monter, descendre ...        
            self.aller(commande)

# -------------------------------------------------------
#               Verbes du joueur
# -------------------------------------------------------

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
        
        objet, origine, _ = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Tu ne vois pas cet objet ici.")
            return
        
        if  origine == "piece":
            print("Tu regardes autour de toi...")
        else:
            print("Tu regardes dans ton inventaire...")
        
        print(objet.description)
        self.afficher_contenu_objet(objet)

    def ouvrir(self, nom_objet):
        objet, _, _ = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("tu ne vois pas cet objet ici")
            return
        
        # cas spécial entrainant une action (trappe, grille, etc.)
        if  "ouvrir" in objet.actions:
            self.executer_action_objet("ouvrir", nom_objet)
            return

        # cas générique : boite, sac, vitrine, etc.    
        if  not objet.props.get("ouvrable", False):
            print("Tu ne peux pas ouvrir ça")
            return
        
        if  objet.etat.get("ouvert", False):
            print(f"{nom_objet} est déjà ouvert")
            return
        
        objet.etat["ouvert"] = True
        print(f"Tu ouvres {nom_objet}.")
        self.afficher_contenu_objet(objet)

    def prendre(self, nom_objet):
        if  nom_objet == "":
            print("Prendre quoi ?")
            return

        objet, origine, source = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Cet objet n'est pas ici")
            return
        
        if  origine == "inventaire":
            print("Tu l'as déjà")
            return
        
        if  not objet.portable:
            print("Tu ne peux pas prendre cet objet")
            return
        
        if  origine == "piece":
            source.objets.remove(objet)

        if  origine == "dans":
            source.contenu.remove(objet)

        if  origine == "sur":
            source.objets_sur.remove(objet)
        
#        piece = self.joueur.position
#        piece.objets.remove(objet)
        self.joueur.inventaire.append(objet)
        print(f"Tu prends {objet.nom}")

    def mettre_dans(self, nom_objet, nom_conteneur):
        objet, origine, source = self.trouver_objet_global(nom_objet)

        if  objet is None or origine != "inventaire":
            print("Tu dois d'abord avoir cet objet")
            return

        conteneur, _, _ = self.trouver_objet_global(nom_conteneur)

        if  conteneur is None:
            print("Tu ne vois pas çe conteneur ici")
            return
        
        if  not conteneur.props.get("conteneur", False):
            print("Ce n'est pas un conteneur")
            return
        
        if  conteneur.props.get("ouvrable", False) and not conteneur.etat.get("ouvert", False):
            print(f"{conteneur.nom} est fermé")
            return
        
        self.joueur.inventaire.remove(objet)
        conteneur.contenu.append(objet)
        print(f"Tu mets {objet.nom} dans {conteneur.nom}.")

    def poser(self, nom_objet):
        if  nom_objet == "":
            print("poser quoi ?")
            return
        
        objet, origine, source = self.trouver_objet_global(nom_objet)

        if  objet is None:
            print("Tu n'as pas cet objet")
            return

        if  origine == "piece":
            print("Cet objet est déjà ici.")
            return
        
        if  origine == "conteneur":
            print("Tu dois d'abord le prendre")
            return
        
        self.joueur.inventaire.remove(objet)
        piece = self.joueur.position
        piece.objets.append(objet)
        print(f"Tu poses {objet.nom}")

    def poser_sur(self, nom_objet, nom_support):
        objet, origine, source = self.trouver_objet_global(nom_objet)

        if  objet is None or origine != "inventaire":
            print("Tu dois d'abord avoir cet objet")
            return

        support, _,_ = self.trouver_objet_global(nom_support)

        if  support is None:
            print("Tu ne vois pas ce support ici")
            return
        
        if  not support.props.get("support", False):
            print("Tu ne peux rien poser dessus.")
            return        
        
        self.joueur.inventaire.remove(objet)
        support.objets_sur.append(objet)
        print(f"Tu poses {objet.nom} sur {support.nom}")

# -------------------------------------------------------
#               Gestion des actions
# -------------------------------------------------------

    def executer_action_objet(self, action, nom_objet):
        piece:Piece = self.joueur.position
        objet:Objet = piece.trouver_objet(nom_objet)              # cherche objet dans Piece

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

        # Modifier propriétés d'objets
        for nom_objet, props in regle.get("set_objet_props", {}).items():
            for obj in piece.objets:
                if  obj.nom == nom_objet:
                    obj.props.update(props)

        # Révéler des sorties
        for direction, id_piece in regle.get("revele_sorties", {}).items():
            piece.ajouter_sortie(direction, self.monde[id_piece])
            self.monde[id_piece].ajouter_sortie("monter", piece)

        print(regle.get("message", "Action effectuée."))

# -------------------------------------------------------
#               Fonctions utilitaires
# -------------------------------------------------------

    def afficher_contenu_objet(self, objet):
#        print("on est dans afficher_contenu_objet")
        if  objet.props.get("support", False):
            if  objet.objets_sur:
                print(f"Sur {objet.nom} tu vois :")
                for obj in objet.objets_sur:
                    print(f"- {obj.description}")
#                    print("normalement il devrait trouver la bouteille ici")

                    # si l'objet est lui-même un conteneur
                    if  obj.props.get("conteneur", False):
                        if  obj.props.get("ouvrable", False) and not obj.etat.get("ouvert", False):
                            continue

                        if  obj.contenu:
                            print(f"   {obj.nom} contient :")
                            for contenu in obj.contenu:
                                print(f"   - {contenu.description}")
                        else:
                            print(f"    {obj.nom} est vide")

        if  objet.props.get("conteneur", False):
            if  objet.props.get("ouvrable", False) and not objet.etat.get("ouvert", False):
                print(f"{objet.nom} est fermé.")
                return
            
            if  objet.contenu:
                print(f"Dans {objet.nom} tu vois :")
                for obj in objet.contenu:
                    print(f"- {obj.description}")
            else:
                print(f"{objet.nom} est vide")

    def decrire_position(self):
        piece:Piece = self.joueur.position

        if  piece.flags.get("sombre", False) and not self.joueur_a_lumiere():
            print("Il fait trop sombre pour voir quoi que ce soit")
            return
        
        piece.decrire()

    def conteneur_accessible(self, objet):
        if  not objet.props.get("conteneur", False):
            return False
        
        if  objet.props.get("ouvrable", False) and not objet.etat.get("ouvert", False):
            return False
        
        return True

    def trouver_objet_global(self, nom_objet):
        piece = self.joueur.position

        objet = piece.trouver_objet(nom_objet)
        if  objet:
            return objet, "piece", piece
        
        objet = self.joueur.trouver_objet(nom_objet)
        if  objet:
            return objet, "inventaire", self.joueur
        
        # objets dans ou sur  des objets de la piece
        for conteneur in piece.objets:
            if  self.conteneur_accessible(conteneur):
                objet = conteneur.trouver_objet_dans(nom_objet)
                if  objet:
                    return objet, "dans", conteneur
                
            if  conteneur.props.get("support", False):
                objet = conteneur.trouver_objet_sur(nom_objet)    
                if  objet:
                    return objet, "sur", conteneur
                
        # objets dans et sur des objets de l'inventaire        
        for conteneur in self.joueur.inventaire:
            if  self.conteneur_accessible(conteneur):
                objet = conteneur.trover_objet_dans(nom_objet)
                if  objet:
                    return objet, "dans", conteneur
                
            if  conteneur.props.get("support", False):
                objet = conteneur.trouver_objet_sur(nom_objet)
                if  objet:
                    return objet, "sur", conteneur
        
        return None, None, None

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
    
# -------------------------------------------------------
#               Évènements automatiques
# -------------------------------------------------------
    
    def decrementer_lampe(self):
        piece = self.joueur.position

        for objet in self.joueur.inventaire:
            if  objet.props.get("lumiere", False) and objet.etat.get("allumee", False):
                objet.etat["duree"] -= 1

                if  objet.etat["duree"] == 3:
                    print("La lampe faiblit")

                if  objet.etat["duree"] <= 0:
                    objet.etat["allumee"] = False
                    objet.etat["duree"] = 0
                    print("La lampe s'éteint")
                    if  piece.flags.get("sombre", False):
                        print("Il fait nuit noire. Tu risques fort de te faire dévorer par un grue.")

    def gerer_obscurite(self):
        piece = self.joueur.position

        if  not piece.flags.get("sombre", False):
            self.tours_dans_le_noir = 0
            return
        
        if  self.joueur_a_lumiere():
            self.tours_dans_le_noir = 0
            return
        
        self.tours_dans_le_noir += 1

        if  self.tours_dans_le_noir == 1:
            print("Il fait noir. Tu risques d'être mangé par une Grue.")
            return

        if  self.tours_dans_le_noir >= 2:
            if  random.randint(1, 100) <= 50:
                print("Tu entends un bruit dans l'obscurité...")
                print()
                print("Une Grue t'a dévoré")
                self.en_cours = False
            else:
                print("Tu tâtonnes dans le noir. Ce n'est pas prudent.")



def creer_monde():
    canyon_vue = Piece(
        "Vue sur le canyon",
        "Tu te trouves au sommet du Grand Canyon, sur sa paroi ouest. De là, vous avez une vue magnifique sur le canyon et sur certaines parties de la rivière Frigid en amont. De l'autre côté du canyon, les parois des White Cliffs rejoignent les imposants remparts des Flathead Mountains à l'est. En remontant le canyon vers le nord, on peut apercevoir les chutes d'Aragain, avec un arc-en-ciel. La puissante rivière Frigid jaillit d'une immense caverne sombre. À l'ouest et au sud, on aperçoit une immense forêt qui s'étend sur des kilomètres à la ronde. Un sentier mène vers le nord-ouest. Il est possible de descendre dans le canyon depuis cet endroit."
    )
    corniche = Piece(
        "Rebord rocheux",
        "Tu te trouves sur une corniche à mi-hauteur de la paroi du canyon. D'ici, vous pouvez voir que le courant principal des chutes d'Aragain serpente le long d'un passage dans lequel il vous est impossible de pénétrer. En contrebas se trouve le fond du canyon. Au-dessus de vous s'étend une autre falaise, qui semble escaladable."
    )
    canyon_bas = Piece(
        "Bas du canyon",
        "Tu te trouves au pied des parois du canyon, qui semblent escaladables à cet endroit. Une petite partie du débit des chutes d'Aragain s'écoule en contrebas. Au nord se trouve un sentier étroit."
    )
    bout_arc_en_ciel = Piece(
        "Bout de l'arc-en-ciel",
        "Tu te trouves sur une petite plage rocheuse, au-delà des chutes, là où la rivière Frigid se poursuit. La plage est étroite en raison de la présence des falaises blanches. Le canyon de la rivière s'ouvre ici et la lumière du soleil pénètre par le haut. Un arc-en-ciel enjambe les chutes à l'est et un sentier étroit continue vers le sud-ouest."
    )

    clairiere_1 = Piece(
        "Clairière",
        "Tu te trouves dans une clairière, entourée de forêt de tous côtés. Un sentier mène vers le sud.    "
    )
    clairiere_2 = Piece(
        "Clairière",
        "tu es dans une petite clairière, sur un sentier forestier bien balisé qui s'étend vers l'est et vers l'ouest"
    )

    foret_1 = Piece(
        "Forêt",
        "C'est une forêt, avec des arbres à perte de vue. À l'est, on dirait qu'il y a de la lumière du soleil"
    )
    foret_2 = Piece(
        "Foret",
        "C'est une forêt peu éclairée, entourée de grands arbres"
    )
    foret_3 = Piece(
        "Forêt",
        "C'est une forêt peu éclairée, entourée de grands arbres"
    )
    foret_4 = Piece(
        "Forêt",
        "La forêt s'éclaircit, laissant apparaître des montagnes infranchissables."
    )
    foret_sentier = Piece(
        "Chemin forestier",
        "C'est un sentier qui serpente à travers une forêt faiblement éclairée. Ici, le sentier s'étend du nord au sud. Un arbre particulièrement imposant, dont certaines branches sont basses, se dresse au bord du sentier."
    )
    arbre = Piece(
        "Dans un arbre",
        "Tu te trouves à environ trois mètres du sol, niché parmi de grosses branches. La branche la plus proche au-dessus de toi est hors de ta portée. À côté de toi, sur la branche, se trouve un petit nid d'oiseau."
    )

    maison_derriere = Piece(
        "Derrière la maison",
        "Tu es derrière la maison blanche. Un sentier mène vers la forêt, à l'est. Dans un coin de la maison, il y a une petite fenêtre légèrement entrouverte."
    )
    maison_nord = Piece(
        "Nord de la maison",
        "Tu es face à la façade nord d'une maison blanche. Il n'y a pas de porte à cet endroit, et toutes les fenêtres sont condamnées. Au nord, un sentier étroit serpente à travers les arbres."
    )
    maison_ouest = Piece(
        "Ouest de la maison",
        "Tu es dans un champ à l'ouest d'une maison blanche dont la porte d'entrée est condamnée."
    )
    maison_sud = Piece(
        "Sud de la maison",
        "Tu es face à la façade sud d'une maison blanche. Il n'y a pas de porte à cet endroit, et toutes les fenêtres sont condamnées."
    )
    cuisine = Piece(
        "Cuisine",
        "Tu te trouves dans la cuisine de la maison blanche. Une table semble avoir servi récemment à la préparation des repas. Un couloir mène vers l'ouest et on aperçoit un escalier sombre qui monte. Une cheminée sombre descend et, à l'est, se trouve une petite fenêtre ouverte."
    )
    grenier = Piece(
        "Grenier",
        "C'est le grenier. La seule sortie est un escalier qui descend."
    )
    salon = Piece(
        "Salon",
        "Tu es dans le salon. Il y a une porte à l'est, une porte en bois ornée d'étranges inscriptions gothiques à l'ouest, qui semble avoir été clouée, une vitrine à trophées et un grand tapis oriental au centre de la pièce."
    )
    cave = Piece(
        "Cave",
        "Tu es dans une cave sombre et humide. L'air sent la pierre froide."
    )

    # Sorties
    canyon_vue.ajouter_sortie("ouest", foret_3)
    canyon_vue.ajouter_sortie("nord-ouest", clairiere_2)
    canyon_vue.ajouter_sortie("descendre", corniche)

    corniche.ajouter_sortie("monter", canyon_vue)
    corniche.ajouter_sortie("descendre", canyon_bas)

    canyon_bas.ajouter_sortie("nord", bout_arc_en_ciel)
    canyon_bas.ajouter_sortie("monter", corniche)

    bout_arc_en_ciel.ajouter_sortie("nord-ouest", canyon_bas)
# manque caché    bout_arc_en_ciel.ajouter_sortie("monter",arc_en_ciel)

    clairiere_1.ajouter_sortie("est", foret_2)
    clairiere_1.ajouter_sortie("sud", foret_sentier)
    clairiere_1.ajouter_sortie("ouest", foret_1)
# manque, caché    clairiere_1.ajouter_objet("descendre", grille_salle)

    clairiere_2.ajouter_sortie("nord", foret_2)
    clairiere_2.ajouter_sortie("est", canyon_vue)
    clairiere_2.ajouter_sortie("sud", foret_3)
    clairiere_2.ajouter_sortie("ouest", maison_derriere)

    foret_1.ajouter_sortie("nord", clairiere_1)
    foret_1.ajouter_sortie("est", foret_sentier)
    foret_1.ajouter_sortie("sud", foret_3)

    foret_2.ajouter_sortie("est", foret_4)
    foret_2.ajouter_sortie("sud", clairiere_2)
    foret_2.ajouter_sortie("ouest", foret_sentier)

    foret_3.ajouter_sortie("nord", clairiere_2)
    foret_3.ajouter_sortie("ouest", foret_1)
    foret_3.ajouter_sortie("nord-ouest", maison_sud)

    foret_4.ajouter_sortie("nord", foret_2)
    foret_4.ajouter_sortie("sud", foret_2)
    foret_4.ajouter_sortie("ouest", foret_2)

    foret_sentier.ajouter_sortie("nord", clairiere_1)
    foret_sentier.ajouter_sortie("est", foret_2)
    foret_sentier.ajouter_sortie("sud", maison_nord)
    foret_sentier.ajouter_sortie("ouest", foret_1)
    foret_sentier.ajouter_sortie("monter", arbre)

    arbre.ajouter_sortie("descendre", foret_sentier)

    maison_derriere.ajouter_sortie("entrer", cuisine)
    maison_derriere.ajouter_sortie("nord", maison_nord)
    maison_derriere.ajouter_sortie("est", clairiere_2)
    maison_derriere.ajouter_sortie("sud", maison_sud)

    maison_nord.ajouter_sortie("nord", foret_sentier)
    maison_nord.ajouter_sortie("est", maison_derriere)
    maison_nord.ajouter_sortie("ouest", maison_ouest)

    maison_ouest.ajouter_sortie("nord", maison_nord)
    maison_ouest.ajouter_sortie("sud", maison_sud)
    maison_ouest.ajouter_sortie("ouest", foret_1)

    maison_sud.ajouter_sortie("est", maison_derriere)
    maison_sud.ajouter_sortie("sud", foret_3)
    maison_sud.ajouter_sortie("ouest", maison_ouest)

    cuisine.ajouter_sortie("est", maison_derriere)
    cuisine.ajouter_sortie("ouest", salon)
    cuisine.ajouter_sortie("monter", grenier)

    grenier.ajouter_sortie("descendre", cuisine)

    salon.ajouter_sortie("est", cuisine)
#   caché : salon.ajouter_sortie("descendre", cave)

    cave.ajouter_sortie("monter", salon)

    # Monde
    monde = {
        "depart": maison_ouest,
        "canyon_vue": canyon_vue,
        "corniche": corniche,
        "canyon_bas": canyon_bas,
        "bout_arc_en_ciel": bout_arc_en_ciel,
        "clairiere_1": clairiere_1,
        "clairiere_2": clairiere_2,
        "foret_1": foret_1,
        "foret_2": foret_2,
        "foret_3": foret_3,
        "foret_4": foret_4,
        "foret_sentier": foret_sentier,
        "arbre": arbre,
        "maison_nord": maison_nord,
        "maison_sud": maison_sud,
        "maison_derriere": maison_derriere,
        "cuisine": cuisine,
        "grenier": grenier,
        "salon": salon,
        "cave": cave
    }

    # Objets
    boite = Objet("boîte aux lettres", "une boîte aux lettres ouverte", portable=False)
    boite.props["conteneur"] = True
    boite.props["ouvrable"] = True
    boite.props["ouverte"] = False
    boite.actions["ouvrir"] = {
        "message": "La boîte aux lettres est ouverte",
        "set_flags": {"boite_ouverte": True}
    }
    depliant = Objet("dépliant", "un dépliant")
    feuilles = Objet("feuilles", "un tas de feuilles sur le sol", portable=False)
    feuilles.actions["deplacer"] = {
        "message": "Il y a une grille solidement fixée au sol",
        "set_flags": {"feuilles_deplacees": True},
        "set_objet_props": {"grille": {"visible": True}}      
    }
    grille = Objet("grille", "une grille fortement fixée au sol", portable=False)
    grille.props = {"visible": False}

    lampe = Objet("lampe", "Une lanterne en laiton fonctionnant à piles")
    lampe.props = {"lumiere": True, "allumable": True}
    lampe.etat["allumee"] = False
    lampe.etat["duree"] = 20            #nombre de tours

    ail = Objet("ail", "une gousse d'ail")
    bouteille = Objet("bouteille", "une bouteille en verre")
    bouteille.props = {"conteneur": True, "ouvrable": True}
    bouteille.etat["ouvert"] = True
    eau = Objet("eau", "une certaine quantité d'eau")
    corde = Objet("corde", "un gros rouleau de corde")              # " est posé dans un coin"
    couteau = Objet("couteau", "un couteau bien aiguisé")
    epee = Objet("épée", "une épée elfique très ancienne")
    repas = Objet("repas", "un repas emballé dans du papier")

    sac = Objet("sac", "un sac brun allongé")
    sac.props = {"conteneur": True, "ouvrable": True}
    sac.etat["ouvert"] = False

    table = Objet("table", "une vieille table en bois")
    table.props = {"support": True}

    vitrine = Objet("vitrine", "une vitrine à trophées")
    vitrine.props = {"conteneur": True, "ouvrable": True, "support": True}
    vitrine.etat["ouvert"] = False

    tapis = Objet("tapis", "un grand tapis d'orient au centre de la pièce")
    tapis.props = {"deplacable": True}
    tapis.actions["deplacer"] = {
        "message": "Tu déplaces le tapis. Une trappe apparaît sur le sol",
        "set_flags": {"tapis_deplace": True, "trappe_visible": True},
        "set_objet_props": {"trappe": {"visible": True}}
    }
# à gérer plus tard    fenetre = object("fenetre", )
    trappe = Objet("trappe", "Une trappe en bois apparaît sur le sol", portable=False)
    trappe.props = {"visible": False}
    trappe.actions["ouvrir"] = {
        "message": "Tu ouvres la trappe. Un escalier descend dans l'obscurité",
        "conditions": {"flags": {"trappe_visible": True}},
        "set_flags": {"trappe_ouverte": True},
        "revele_sorties": {"descendre": "cave"}
    }

    # Localisation objets
    maison_ouest.ajouter_objet(boite)
    
    clairiere_1.ajouter_objet(feuilles)
    clairiere_1.ajouter_objet(grille)

#    cuisine.ajouter_objet(sac)
    cuisine.ajouter_objet(table)
#    salon.ajouter_objet(lampe)
    salon.ajouter_objet(tapis)
    salon.ajouter_objet(trappe)
    salon.ajouter_objet(vitrine)
    grenier.ajouter_objet(corde)
    grenier.ajouter_objet(couteau)

    # Initialisation du contenu des objets
    boite.contenu.append(depliant)
    sac.contenu.append(ail)
    sac.contenu.append(repas)
    table.objets_sur.append(sac)
    table.objets_sur.append(bouteille)
    bouteille.contenu.append(eau)
    vitrine.objets_sur.append(epee)
    vitrine.objets_sur.append(lampe)

    # États locaux (pièces)
    cave.flags["sombre"] = True
    clairiere_1.flags["feuilles_deplacees"] = False
    salon.flags["tapis_déplacé"] = False
    salon.flags["trappe_visible"] = False
    salon.flags["trappe_ouverte"] = False


    # Point d'entrée        
    return monde    


# main
if __name__ == "__main__" :
    monde = creer_monde()
    jeu = Engine(monde)
    jeu.lancer()