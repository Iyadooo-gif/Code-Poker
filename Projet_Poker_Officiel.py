import random

class Carte:
    def __init__(self, valeur, couleur):
        self.valeur = valeur
        self.couleur = couleur

    def __repr__(self):
        valeurs = {11: "J", 12: "Q", 13: "K", 14: "A"}
        valeur = valeurs.get(self.valeur, str(self.valeur))
        return f"{valeur}{self.couleur}"

class JeuDeCartes:
    def __init__(self):
        couleurs = ['♠', '♥', '♦', '♣']
        valeurs = list(range(2, 15))
        self.cartes = [Carte(valeur, couleur) for valeur in valeurs for couleur in couleurs]
        random.shuffle(self.cartes)

    def distribuer(self):
        return self.cartes.pop()

class Main:
    def __init__(self):
        self.cartes = []

    def ajouter_carte(self, carte):
        self.cartes.append(carte)

    def evaluer(self, cartes_communes):
        cartes = self.cartes + cartes_communes
        valeurs = sorted([carte.valeur for carte in cartes], reverse=True)
        compte = {valeur: valeurs.count(valeur) for valeur in valeurs}

        # Évaluation des combinaisons
        if self.quinte_flush(cartes):
            return 900 + max(valeurs)
        if 4 in compte.values():
            return 800 + max(k for k, v in compte.items() if v == 4)
        if 3 in compte.values() and 2 in compte.values():
            return 700 + max(k for k, v in compte.items() if v == 3)
        if self.couleur(cartes):
            return 600 + max(valeurs)
        if self.quinte(cartes):
            return 500 + max(valeurs)
        if 3 in compte.values():
            return 400 + max(k for k, v in compte.items() if v == 3)
        if list(compte.values()).count(2) == 2:
            return 300 + max(k for k, v in compte.items() if v == 2)
        if 2 in compte.values():
            return 200 + max(k for k, v in compte.items() if v == 2)
        return 100 + max(valeurs)

    def quinte(self, cartes):
        valeurs = sorted(set(carte.valeur for carte in cartes))
        for i in range(len(valeurs) - 4):
            if valeurs[i:i+5] == list(range(valeurs[i], valeurs[i] + 5)):
                return True
        return False

    def couleur(self, cartes):
        couleurs = [carte.couleur for carte in cartes]
        return any(couleurs.count(couleur) >= 5 for couleur in set(couleurs))

    def quinte_flush(self, cartes):
        couleurs = {couleur: [] for couleur in ['♠', '♥', '♦', '♣']}
        for carte in cartes:
            couleurs[carte.couleur].append(carte.valeur)
        for valeurs in couleurs.values():
            valeurs = sorted(set(valeurs))
            for i in range(len(valeurs) - 4):
                if valeurs[i:i+5] == list(range(valeurs[i], valeurs[i] + 5)):
                    return True
        return False

class Joueur:
    def __init__(self, nom):
        self.nom = nom
        self.main = Main()
        self.jetons = 100
        self.en_jeu = True

    def miser(self, montant):
        self.jetons -= montant

    def se_coucher(self):
        self.en_jeu = False

class TableDePoker:
    def __init__(self):
        self.joueurs = []
        self.jeu_de_cartes = JeuDeCartes()
        self.pot = 0
        self.cartes_communes = []
        self.partie_terminee = False

    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)

    def debuter_partie(self):
        print("La partie commence !")
        for joueur in self.joueurs:
            joueur.main.ajouter_carte(self.jeu_de_cartes.distribuer())
            joueur.main.ajouter_carte(self.jeu_de_cartes.distribuer())
        self.afficher_cartes_joueurs()

    def afficher_cartes_joueurs(self):
        for joueur in self.joueurs:
            if joueur.nom == "Humain":
                print(f"{joueur.nom} : {joueur.main.cartes}")
            else:
                print(f"{joueur.nom} : [?], [?]")

    def afficher_table(self):
        print("Cartes communes :", ', '.join(str(carte) for carte in self.cartes_communes))

    def tour_de_mise(self, mise_minimale):
        for joueur in self.joueurs:
            if joueur.en_jeu and not self.partie_terminee:
                if joueur.nom == "Humain":
                    self.humain_jouer(joueur, mise_minimale)
                else:
                    self.ia_jouer(joueur, mise_minimale)
            self.verifier_fin_partie()
            if self.partie_terminee:
                break

    def humain_jouer(self, joueur, mise_minimale):
        print(f"\nVos cartes : {joueur.main.cartes}")
        print(f"Pot actuel : {self.pot}")
        print(f"Mise minimale : {mise_minimale} jetons")
        action = input("Que voulez-vous faire ? (miser, suivre, relancer, se coucher) : ").lower()
        if action in ["miser", "relancer"]:
            mise = int(input("Combien voulez-vous miser ? : "))
            if mise >= mise_minimale:
                joueur.miser(mise)
                self.pot += mise
            else:
                print(f"La mise doit être au moins de {mise_minimale} jetons.")
        elif action == "suivre":
            joueur.miser(mise_minimale)
            self.pot += mise_minimale
        elif action == "se coucher":
            joueur.se_coucher()
            print(f"{joueur.nom} s'est couché.")
            self.partie_terminee = True

    def ia_jouer(self, joueur, mise_minimale):
        print("\nL'IA réfléchit...")
        main_valeur = joueur.main.evaluer(self.cartes_communes)
        if main_valeur > 500:
            action = "relancer" if mise_minimale < 20 else "suivre"
        elif main_valeur > 200:
            action = "suivre"
        else:
            action = "se coucher" if mise_minimale > 10 else "suivre"

        if action == "relancer":
            mise = mise_minimale + 10
            print(f"L'IA relance avec {mise} jetons.")
            joueur.miser(mise)
            self.pot += mise
        elif action == "suivre":
            print(f"L'IA suit avec {mise_minimale} jetons.")
            joueur.miser(mise_minimale)
            self.pot += mise_minimale
        elif action == "se coucher":
            print("L'IA s'est couchée.")
            joueur.se_coucher()
            self.partie_terminee = True

    def verifier_fin_partie(self):
        joueurs_en_jeu = [j for j in self.joueurs if j.en_jeu]
        if len(joueurs_en_jeu) == 1:
            gagnant = joueurs_en_jeu[0]
            print(f"\n{gagnant.nom} gagne la partie avec {self.pot} jetons dans le pot !")
            self.partie_terminee = True

    def jouer_tour(self, nombre_cartes):
        for _ in range(nombre_cartes):
            self.cartes_communes.append(self.jeu_de_cartes.distribuer())
        self.afficher_table()
        self.tour_de_mise(10)

    def determiner_gagnant(self):
        if self.partie_terminee:
            return
        scores = {joueur: joueur.main.evaluer(self.cartes_communes) for joueur in self.joueurs if joueur.en_jeu}
        gagnant = max(scores, key=scores.get)
        print(f"\n{gagnant.nom} gagne avec {gagnant.main.cartes} !")
        print("Cartes communes :", self.cartes_communes)
        for joueur in self.joueurs:
            print(f"{joueur.nom} : {joueur.main.cartes}")

def main():
    table = TableDePoker()
    humain = Joueur("Humain")
    ia = Joueur("IA")

    table.ajouter_joueur(humain)
    table.ajouter_joueur(ia)

    table.debuter_partie()

    if not table.partie_terminee:
        table.jouer_tour(3)
    if not table.partie_terminee:
        table.jouer_tour(1)
    if not table.partie_terminee:
        table.jouer_tour(1)

    if not table.partie_terminee:
        table.determiner_gagnant()

if __name__ == "__main__":
    main()
