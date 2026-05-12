import random   # après split en plusieurs fichiers,mettre dans Engine.py, ainsi que les aliases

ALIASES = {
    "n": "nord",
    "s": "sud",
    "e": "est",
    "o": "ouest",
    "w": "ouest",
    "m": "monter",
    "u": "monter",
    "grimper": "monter",
    "d": "descendre"
}
DIRECTIONS = {
    "nord", "est", "sud", "ouest",
    "nord-est", "sud-est", "sud-ouest", "nord-ouest",
    "monter", "descendre", "entrer", "sortir"
}

class Piece:
    def __init__(self, nom, description):
        self.nom = nom
        self.description = description
        self.sorties = {}
        self.objets = []
        self.flags = {}
        self.visitee = False

    def ajouter_sortie(self, direction, piece_destination):
        self.sorties[direction] = piece_destination

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def trouver_objet(self, nom):
        for objet in self.objets:
            if  objet.nom == nom and objet.props.get("visible", True):
                return objet
        return None

    def decrire(self):
        print()
        print(self.nom)
        print(self.description)
        self.decrire_objets()

#        if self.sorties:
#            print("Sorties :", ", ".join(self.sorties.keys()))

    def decrire_objets(self, long = False):
        for objet in self.objets:
            if  objet.props.get("visible", True):
                self.decrire_objet_visible(objet, long)

    def decrire_objet_visible(self, objet, long = False):                    
            texte = objet.decrire() if long else objet.decrire_court()
            print(f"Il y a {texte} ici")

            self.decrire_objets_sur(objet)
            self.decrire_objets_dans(objet)

    def decrire_objets_sur(self, objet):
        if  not objet.props.get("support", False):
            return
        
        if  not objet.objets_sur:
            return
        
        print(f"\nSur {objet.nom}, tu vois :")

        for obj in objet.objets_sur:
            print(f"- {obj.decrire_court()}")
            self.decrire_objets_dans(obj, indentation = "   ")

    def decrire_objets_dans(self, objet, indentation = ""):
        if  not objet.props.get("conteneur", False):
            return
        
        if  objet.props.get("ouvrable", False) and not objet.etat.get("ouvert", False):
            return
        
        if  not objet.contenu:
            return
        
        print(f"{indentation}Dans {objet}, tu vois :")

        for obj in objet.contenu:
            print(f"{indentation}- {obj.decrire_court()}")


class Objet:
    def __init__(self, nom, description, portable = True, description_courte = None):
        self.nom = nom
        self.description = description
        self.description_courte = description_courte or description
        self.deja_vu = False
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
    
    def decrire(self):
        if not self.deja_vu:
            self.deja_vu = True
            texte = self.description
        else:
            texte = self.description_courte

        if  self.props.get("ouvrable", False):
            if  self.etat.get("ouvert", False):
                texte += " ouverte"
            else:
                texte += " fermée"

        return texte
    
    def decrire_court(self):
        texte = self.description_courte

        if  self.props.get("ouvrable", False):
            if  self.etat.get("ouvert", False):
                texte += " ouverte"
            else:
                texte += " fermée"

        return texte
    
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
        self.erreur_verbe = 0
        self.nb_morts = 0
        self.score = 0
        self.points_obtenus = set()

# -------------------------------------------------------
#               Coeur du moteur
# -------------------------------------------------------

    def lancer(self):
        print("Bienvenue")
        print("Tape 'aide' pour voir les commandes.\n")
        self.decrire_position()

        while self.en_cours:
            commande = input("\n>").strip().lower()
            self.traiter_commande(commande)

            if  self.en_cours:
                self.decrementer_lampe()
                self.gerer_obscurite()
                self.gerer_ambiance()

    def traiter_commande(self, commande):
        if  commande == "":
            return
        
        commande_valide = False
        
        if  commande in ("quit", "exit"):
            self.en_cours = False
            print("Fin de la partie")
            return
        
        if  commande in ("aide", "help"):
            self.afficher_aide()
            return
        
        if  commande in ("inventaire", "inv", "i"):
            self.afficher_inventaire()
            return
        
        if  commande in("regarder", "look"):
            self.decrire_position(complet = True)
            return
        
        # traitement mettre ou poser un objet dans ou sur un conteneur
        if  commande.startswith("mettre ") and " dans " in commande:
            reste = commande.replace("mettre ", "" , 1)
            nom_objet, nom_conteneur = reste.split(" dans ", 1)
            commande_valide = True
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
        verbe = self.normaliser_direction(verbe)
        complement = " ".join(mots[1:])

        if  verbe in ("prendre", "take"):
            commande_valide = True
            self.prendre(complement)
        elif verbe in ("déplacer", "soulever"):
            self.executer_action_objet("deplacer", complement)
        elif verbe == "allumer":
            self.allumer(complement)
        elif verbe == "examiner":
            commande_valide = True
            self.examiner(complement)
        elif verbe == "ouvrir":
            self.ouvrir(complement)
        elif verbe == "poser":
            commande_valide = True
            self.poser(complement)
        elif verbe in DIRECTIONS:
            commande_valide = True
            self.aller(verbe)
        else:
            print("je ne connais pas cette commande")

        # gestion erreurs
        if  commande_valide:
            self.erreur_verbe = 0
        else:
            self.erreur_verbe += 1
        
            if  self.erreur_verbe > 3:
                print("\n Tu sembles un peu perdu...\n")
                self.afficher_aide()
                self.erreur_verbe = 0

# -------------------------------------------------------
#               Verbes du joueur
# -------------------------------------------------------

    def afficher_aide(self):
        print("Commandes disponibles :")
        print("Directions :")
        print("nord, sud, est, ouest, nord-est, nord-ouest, sud-ouest, nord-ouest")
        print("entrer, sortir, monter, descendre\n")
        print("Verbes courants :")
        print("prendre, poser, poser objet sur support, mettre objet dans conteneur")
        print("déplacer, ouvrir, allumer\n")
        print("Commandes de jeu :")
        print("regarder : décrit la pièce actuelle")
        print("examiner : donne une description détaillée d'un objet")
        print("aide, inventaire, quit")

    def afficher_inventaire(self):
        if  self.joueur.inventaire:
            print("Tu portes :")
            for obj in self.joueur.inventaire:
                print(f"- {obj.decrire_court()}")
        else:
            print("Tu ne portes rien.")

    def aller(self, direction):
        piece = self.joueur.position

        if  direction in piece.sorties:
            ancienne_piece = self.joueur.position               # ajouté pour cas spécial trappe qui se referme
            self.joueur.position = piece.sorties[direction]
            nouvelle_piece = self.joueur.position

            # ajout cas spécial trappe qui se referme, a rendre générique plus tard
            
            if  ancienne_piece.nom == "Salon" and self.joueur.position.nom == "Cave":
                ancienne_piece.flags["trappe_ouverte"] = False

                if  "descendre" in ancienne_piece.sorties:
                    del ancienne_piece.sorties["descendre"]

                if  "monter" in self.joueur.position.sorties:
                    del self.joueur.position.sorties["monter"]

                print("La trappe se referme dans un grand fracas, et tu entends quelqu'un la verrouiller.")
            # fin de l'ajout

            score = nouvelle_piece.flags.get("score_entree")
            if  score:
                self.ajouter_score(score["cle"], score["points"])

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

        if  not objet.etat.get("deja_ouvert", False):
            message = objet.props.get("message_premiere_ouverture")
            if  message:
                print(message)
            else:
                print(f"Tu ouvres {objet.nom}.")
            objet.etat["deja_ouvert"] = True
        else:
            print(f"Tu ouvres {objet.nom}.")

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
        
        score = objet.props.get("score_prise")
        if  score:
            self.ajouter_score(score["cle"], score["points"])
        
        if  origine == "piece":
            source.objets.remove(objet)

        if  origine == "dans":
            source.contenu.remove(objet)

        if  origine == "sur":
            source.objets_sur.remove(objet)

        if  origine == "dans" and source.nom == "vitrine":
            score = objet.props.get("score_vitrine")
            if  score and objet.etat.get("dans_vitrine", False):
                self.modifier_score(-score["points"])
                objet.etat["dans_vitrine"] = False
        
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

        if  conteneur.nom == "vitrine":
            score = objet.props.get("score_vitrine")
            if  score:
                self.modifier_score(score["points"])
                objet.etat["dans_vitrine"] = True

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
        
        if origine in ("dans", "sur"):
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

    def normaliser_direction(self, direction):
        return ALIASES.get(direction, direction)

    def afficher_contenu_objet(self, objet):
        if  objet.props.get("support", False):
            if  objet.objets_sur:
                print(f"\nSur {objet.nom} tu vois :")
                for obj in objet.objets_sur:
                    print(f"- {obj.description}")

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

    def ajouter_score(self, cle, points):
        if  cle in self.points_obtenus:
            return
        
        self.points_obtenus.add(cle)
        self.score += points
        print(f"Score : +{points} points. Total : {self.score}")

    def modifier_score(self, points):
        self.score += points
        print(f"Score : {self.score}")

    def decrire_position(self, complet = False):
        piece:Piece = self.joueur.position

        if  piece.flags.get("sombre", False) and not self.joueur_a_lumiere():
            print("Il fait trop sombre pour voir quoi que ce soit")
            return
        
        print()
        print(piece.nom)
        
        if  complet or not piece.visitee:
            print(piece.description)
            piece.visitee = True
            piece.decrire_objets(long = True)
        else:
            piece.decrire_objets(long = False)

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
                objet = conteneur.trouver_objet_dans(nom_objet)
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
                print()
                print("Oh, non !")
                print("Tu es tombé entre les crocs baveux d'un grue qui t'attendait en embuscade !")
                print()
                print("   ****  Tu es mort  ****")
                self.mourir()
            else:
                print("Tu tâtonnes dans le noir. Ce n'est pas prudent.")

    def mourir(self):
        self.nb_morts += 1

        if  self.nb_morts == 1:
            print("\nBon, voyons voir… Eh bien, tu mérites sans doute une autre chance. Je ne peux pas te remettre complètement d'aplomb, mais on ne peut pas tout avoir.\n")
            self.perdre_inventaire()

            lieux = [self.monde["foret_1"], self.monde["foret_2"], self.monde["foret_3"], self.monde["foret_4"],]
            self.joueur.position = random.choice(lieux)
            self.tours_dans_le_noir = 0

            self.decrire_position()
            return
        
        print("\nDommage, je t'avais pourtant donné une seconde chance !")
        self.en_cours = False

    def perdre_inventaire(self):
        lieux_foret = [self.monde["foret_1"], self.monde["foret_2"], self.monde["foret_3"], self.monde["foret_4"], self.monde["clairiere_1"], self.monde["clairiere_2"]]

        inventaire = self.joueur.inventaire[:]              # attention : [:] parcourt une copie de la liste : indispensable dans une boucle

        # gérer la lampe
        reste = []
        for objet in inventaire:
            if  objet.nom == "lampe":
                self.joueur.inventaire.remove(objet)
                self.monde["maison_derriere"].objets.append(objet)
            else:
                reste.append(objet)      # crée une liste reste pour éviter que la lampe soit enlevée deux fois

        # dispatcher environ la moitié des autres objets
        for objet in reste:            
            if  random.randint(1, 100) <= 50:
                self.joueur.inventaire.remove(objet)
                lieu = random.choice(lieux_foret)
                lieu.objets.append(objet)

    def gerer_ambiance(self):
        piece = self.joueur.position

        if  piece.flags.get("foret", False):
            if  random.randint(1, 100) <= 10:
                print("On entend au loin le gazouillis d'un oiseau chanteur.")



def creer_monde():
    monde = creer_pieces()
    connecter_pieces(monde)

    objets = creer_objets()
    placer_objets(monde, objets)
    initialiser_contenus(objets)
    initialiser_flags(monde)
    initialiser_scores(monde, objets)

    # Point d'entrée        
    return monde    


def creer_pieces():    
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
        "Tu es dans une cave sombre et humide, avec un passage étroit menant vers le nord et un passage à quatre pattes vers le sud. À l'ouest se trouve le pied d'une rampe métallique escarpée qu'il est impossible d'escalader."
    )
    gouffre_est = Piece(
        "À l'est du gouffre",
        "Tu te trouves au bord est d'un gouffre dont le fond est invisible. Un passage étroit mène vers le nord, tandis que le chemin sur lequel tu te trouves continue vers l'est."
    )
    galerie = Piece(
        "Galerie d'art",
        "Voici une galerie d'art. La plupart des tableaux ont été volés par des vandales au goût exceptionnel. Ces derniers se sont enfuis par la sortie nord ou par la sortie ouest."
    )
    studio = Piece(
        "Studio",
        "Il semble que ce lieu ait été l'atelier d'un artiste. Les murs et le sol sont éclaboussés de peinture de 69 couleurs différentes. Curieusement, aucun objet de valeur n'est accroché ici. À l'extrémité sud de la pièce se trouve une porte ouverte (elle aussi recouverte de peinture). Une cheminée sombre et étroite part de la cheminée ; même si tu pouvais y monter, il semble peu probable que tu puisses en redescendre."
    )
    salle_troll = Piece(
        "Salle du troll",
        "C'est une petite pièce avec des passages menant à l'est et au sud, ainsi qu'un trou sinistre s'ouvrant vers l'ouest. Des taches de sang et de profondes éraflures (probablement causées par une hache) marquent les murs.\nUn troll à l'air repoussant, brandissant une hache ensanglantée, bloque tous les passages menant hors de la pièce.\nLe coup puissant du troll te fait tomber à genoux.\nSauve-toi par le sud !"
    )

    return {
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
        "maison_ouest": maison_ouest,
        "cuisine": cuisine,
        "grenier": grenier,
        "salon": salon,
        "cave": cave,
        "gouffre_est": gouffre_est,
        "galerie": galerie,
        "studio": studio,
        "salle_troll": salle_troll
    }

    # Sorties
def connecter_pieces(monde):
    monde["canyon_vue"].ajouter_sortie("ouest", monde["foret_3"])
    monde["canyon_vue"].ajouter_sortie("nord-ouest", monde["clairiere_2"])
    monde["canyon_vue"].ajouter_sortie("descendre", monde["corniche"])

    monde["corniche"].ajouter_sortie("monter", monde["canyon_vue"])
    monde["corniche"].ajouter_sortie("descendre", monde["canyon_bas"])

    monde["canyon_bas"].ajouter_sortie("nord", monde["bout_arc_en_ciel"])
    monde["canyon_bas"].ajouter_sortie("monter", monde["corniche"])

    monde["bout_arc_en_ciel"].ajouter_sortie("sud-ouest", monde["canyon_bas"])
# manque caché    bout_arc_en_ciel.ajouter_sortie("monter",arc_en_ciel)

    monde["clairiere_1"].ajouter_sortie("est", monde["foret_2"])
    monde["clairiere_1"].ajouter_sortie("sud", monde["foret_sentier"])
    monde["clairiere_1"].ajouter_sortie("ouest", monde["foret_1"])
# manque, caché    clairiere_1.ajouter_objet("descendre", grille_salle)

    monde["clairiere_2"].ajouter_sortie("nord", monde["foret_2"])
    monde["clairiere_2"].ajouter_sortie("est", monde["canyon_vue"])
    monde["clairiere_2"].ajouter_sortie("sud", monde["foret_3"])
    monde["clairiere_2"].ajouter_sortie("ouest", monde["maison_derriere"])

    monde["foret_1"].ajouter_sortie("nord", monde["clairiere_1"])
    monde["foret_1"].ajouter_sortie("est", monde["foret_sentier"])
    monde["foret_1"].ajouter_sortie("sud", monde["foret_3"])

    monde["foret_2"].ajouter_sortie("est", monde["foret_4"])
    monde["foret_2"].ajouter_sortie("sud", monde["clairiere_2"])
    monde["foret_2"].ajouter_sortie("ouest", monde["foret_sentier"])

    monde["foret_3"].ajouter_sortie("nord", monde["clairiere_2"])
    monde["foret_3"].ajouter_sortie("ouest", monde["foret_1"])
    monde["foret_3"].ajouter_sortie("nord-ouest", monde["maison_sud"])

    monde["foret_4"].ajouter_sortie("nord", monde["foret_2"])
    monde["foret_4"].ajouter_sortie("sud", monde["foret_2"])
    monde["foret_4"].ajouter_sortie("ouest", monde["foret_2"])

    monde["foret_sentier"].ajouter_sortie("nord", monde["clairiere_1"])
    monde["foret_sentier"].ajouter_sortie("est", monde["foret_2"])
    monde["foret_sentier"].ajouter_sortie("sud", monde["maison_nord"])
    monde["foret_sentier"].ajouter_sortie("ouest", monde["foret_1"])
    monde["foret_sentier"].ajouter_sortie("monter", monde["arbre"])

    monde["arbre"].ajouter_sortie("descendre", monde["foret_sentier"])

    monde["maison_derriere"].ajouter_sortie("entrer", monde["cuisine"])
    monde["maison_derriere"].ajouter_sortie("nord", monde["maison_nord"])
    monde["maison_derriere"].ajouter_sortie("est", monde["clairiere_2"])
    monde["maison_derriere"].ajouter_sortie("sud", monde["maison_sud"])

    monde["maison_nord"].ajouter_sortie("nord", monde["foret_sentier"])
    monde["maison_nord"].ajouter_sortie("est", monde["maison_derriere"])
    monde["maison_nord"].ajouter_sortie("ouest", monde["maison_ouest"])

    monde["maison_ouest"].ajouter_sortie("nord", monde["maison_nord"])
    monde["maison_ouest"].ajouter_sortie("sud", monde["maison_sud"])
    monde["maison_ouest"].ajouter_sortie("ouest", monde["foret_1"])

    monde["maison_sud"].ajouter_sortie("est", monde["maison_derriere"])
    monde["maison_sud"].ajouter_sortie("sud", monde["foret_3"])
    monde["maison_sud"].ajouter_sortie("ouest", monde["maison_ouest"])

    monde["cuisine"].ajouter_sortie("est", monde["maison_derriere"])
    monde["cuisine"].ajouter_sortie("sortir", monde["maison_derriere"])
    monde["cuisine"].ajouter_sortie("ouest", monde["salon"])
    monde["cuisine"].ajouter_sortie("monter", monde["grenier"])

    monde["grenier"].ajouter_sortie("descendre", monde["cuisine"])

    monde["salon"].ajouter_sortie("est", monde["cuisine"])
#   caché : salon.ajouter_sortie("descendre", cave)

    monde["cave"].ajouter_sortie("nord", monde["salle_troll"])
    monde["cave"].ajouter_sortie("monter", monde["salon"])
    monde["cave"].ajouter_sortie("sud", monde["gouffre_est"])

    monde["gouffre_est"].ajouter_sortie("nord", monde["cave"])
    monde["gouffre_est"].ajouter_sortie("est", monde["galerie"])

    monde["galerie"].ajouter_sortie("nord", monde["studio"])
    monde["galerie"].ajouter_sortie("ouest", monde["gouffre_est"])

    monde["studio"].ajouter_sortie("sud", monde["galerie"])
    monde["studio"].ajouter_sortie("monter", monde["cuisine"])

    monde["salle_troll"].ajouter_sortie("sud", monde["cave"])

    # Objets
def creer_objets():
    objets = {}

    boite = Objet("boîte aux lettres", "une boîte aux lettres", portable=False)
    objets["boite"] = boite
    boite.props = {"conteneur": True, "ouvrable": True}
    boite.etat["ouvert"] = False

    depliant = Objet("dépliant", "un dépliant sur lequel est écrit : BIENVENUE A ZORK")
    objets["depliant"] = depliant
    feuilles = Objet("feuilles", "un tas de feuilles sur le sol", portable=False)
    objets["feuilles"] = feuilles
    feuilles.actions["deplacer"] = {
        "message": "Il y a une grille solidement fixée au sol",
        "set_flags": {"feuilles_deplacees": True},
        "set_objet_props": {"grille": {"visible": True}}      
    }
    oeuf = Objet("oeuf", "Un gros œuf incrusté de pierres précieuses, apparemment ramassé par un oiseau chanteur sans progéniture. L'œuf est recouvert d'une fine incrustation d'or et orné de lapis-lazuli et de nacre. Contrairement à la plupart des œufs, celui-ci est articulé et se ferme à l'aide d'un fermoir d'apparence délicate. L'œuf semble extrêmement fragile.",
                 description_courte = "un oeuf doré incrusté de pierres précieuses")
    objets["oeuf"] = oeuf
    grille = Objet("grille", "une grille fortement fixée au sol", portable=False)
    objets["grille"] = grille
    grille.props = {"visible": False}

    fenetre = Objet("fenêtre", "une petite fenêtre")
    objets["fenetre"] = fenetre
    fenetre.props = {"ouvrable": True, "message_premiere_ouverture": "Avec un grand effort, tu parviens à ouvrir la fenêtre"}
    fenetre.etat = {"ouvert": False, "deja_ouvert": False}

    lampe = Objet("lampe", "Une lampe en laiton fonctionnant à piles")
    objets["lampe"] = lampe
    lampe.props = {"lumiere": True, "allumable": True}
    lampe.etat["allumee"] = False
    lampe.etat["duree"] = 20            #nombre de tours

    ail = Objet("ail", "une gousse d'ail")
    objets["ail"] = ail
    bouteille = Objet("bouteille", "une bouteille en verre")
    objets["bouteille"] = bouteille
    bouteille.props = {"conteneur": True, "ouvrable": True}
    bouteille.etat["ouvert"] = True
    eau = Objet("eau", "une certaine quantité d'eau")
    objets["eau"] = eau
    corde = Objet("corde", "Un gros rouleau de corde  est posé dans un coin du grenier", description_courte = "un gros rouleau de corde")
    objets["corde"] = corde
    couteau = Objet("couteau", "un couteau bien aiguisé")
    objets["couteau"] = couteau
    epee = Objet("épée", "une épée elfique très ancienne")
    objets["epee"] = epee
    repas = Objet("repas", "un repas emballé dans du papier")
    objets["repas"] = repas

    sac = Objet("sac", "un sac brun allongé")
    objets["sac"] = sac
    sac.props = {"conteneur": True, "ouvrable": True}
    sac.etat["ouvert"] = False

    table = Objet("table", "une vieille table en bois")
    objets["table"] = table
    table.props = {"support": True}

    vitrine = Objet("vitrine", "une vitrine à trophées")
    objets["vitrine"] = vitrine
    vitrine.props = {"conteneur": True, "ouvrable": True, "support": True}
    vitrine.etat["ouvert"] = False

    tapis = Objet("tapis", "un grand tapis d'orient au centre de la pièce")
    objets["tapis"] = tapis
    tapis.props = {"deplacable": True}
    tapis.actions["deplacer"] = {
        "message": "Tu déplaces le tapis. Une trappe apparaît sur le sol",
        "set_flags": {"tapis_deplace": True, "trappe_visible": True},
        "set_objet_props": {"trappe": {"visible": True}}
    }

    trappe = Objet("trappe", "Une trappe en bois apparaît sur le sol", portable=False)
    objets["trappe"] = trappe
    trappe.props = {"visible": False}
    trappe.actions["ouvrir"] = {
        "message": "Tu ouvres la trappe. Un escalier descend dans l'obscurité",
        "conditions": {"flags": {"trappe_visible": True}},
        "set_flags": {"trappe_ouverte": True},
        "revele_sorties": {"descendre": "cave"}
    }

    tableau = Objet("tableau", "Heureusement, il te reste une chance de jouer les vandales, car sur le mur du fond se trouve un tableau d'une beauté sans pareille.",
                     description_courte = "un tableau d'une beauté sans pareille")
    objets["tableau"] = tableau
    
    return objets

    # Localisation objets
def placer_objets(monde, objets):
    monde["maison_ouest"].ajouter_objet(objets["boite"])
    monde["maison_derriere"].ajouter_objet(objets["fenetre"])
    
    monde["clairiere_1"].ajouter_objet(objets["feuilles"])
    monde["clairiere_1"].ajouter_objet(objets["grille"])
    monde["arbre"].ajouter_objet(objets["oeuf"])

    monde["cuisine"].ajouter_objet(objets["fenetre"])
    monde["cuisine"].ajouter_objet(objets["table"])
    monde["salon"].ajouter_objet(objets["tapis"])
    monde["salon"].ajouter_objet(objets["trappe"])
    monde["salon"].ajouter_objet(objets["vitrine"])
    monde["grenier"].ajouter_objet(objets["corde"])
    monde["grenier"].ajouter_objet(objets["couteau"])

    monde["galerie"].ajouter_objet(objets["tableau"])

    # Initialisation du contenu des objets
def initialiser_contenus(objets):
    objets["boite"].contenu.append(objets["depliant"])
    objets["sac"].contenu.append( objets["ail"])
    objets["sac"].contenu.append( objets["repas"])
    objets["table"].objets_sur.append( objets["sac"])
    objets["table"].objets_sur.append( objets["bouteille"])
    objets["bouteille"].contenu.append( objets["eau"])
    objets["vitrine"].objets_sur.append( objets["epee"])
    objets["vitrine"].objets_sur.append( objets["lampe"])

    # États locaux (pièces)
def initialiser_flags(monde):
    monde["cave"].flags["sombre"] = True
    monde["clairiere_1"].flags["feuilles_deplacees"] = False
    monde["clairiere_1"].flags["foret"] = True
    monde["clairiere_2"].flags["foret"] = True
    monde["foret_1"].flags["foret"] = True
    monde["foret_2"].flags["foret"] = True
    monde["foret_3"].flags["foret"] = True
    monde["foret_4"].flags["foret"] = True
    monde["foret_sentier"].flags["foret"] = True
    monde["gouffre_est"].flags["sombre"] = True
    monde["galerie"].flags["sombre"] = True
    monde["studio"].flags["sombre"] = True
    monde["salle_troll"].flags["sombre"] = True
    monde["salon"].flags["tapis_deplace"] = False
    monde["salon"].flags["trappe_visible"] = False
    monde["salon"].flags["trappe_ouverte"] = False

    # Trésors et actions rapportant des points
def initialiser_scores(monde, objets):
    monde["cuisine"].flags["score_entree"] = {"cle": "entree_maison", "points": 10}
    monde["cave"].flags["score_entree"] = {"cle": "entree_cave", "points": 25}

    objets["oeuf"].props["score_prise"] = {"cle": "prise_oeuf", "points": 5}
    objets["oeuf"].props["score_vitrine"] = {"cle": "vitrine_oeuf", "points": 5}
    objets["tableau"].props["score_prise"] = {"cle": "prise_tableau", "points": 4}
    objets["tableau"].props["score_vitrine"] = {"cle": "vitrine_tableau", "points": 6}



# main
if __name__ == "__main__" :
    monde = creer_monde()
    jeu = Engine(monde)
    jeu.lancer()