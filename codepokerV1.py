import random
from collections import Counter

# Classe représentant une carte
class Carte:
    def __init__(self, couleur, valeur):
        self.couleur = couleur
        self.valeur = valeur

    def __str__(self):
        return f"{self.valeur} de {self.couleur}"

# Classe représentant le jeu de cartes
class JeuDeCartes:
    def __init__(self):
        couleurs = ['Coeur', 'Carreau', 'Trèfle', 'Pique']
        valeurs = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Valet', 'Dame', 'Roi', 'As']
        self.cartes = [Carte(couleur, valeur) for couleur in couleurs for valeur in valeurs]
        self.melanger()

    def melanger(self):
        random.shuffle(self.cartes)

    def distribuer(self):
        return self.cartes.pop()

# Classe représentant la main d'un joueur
class Main:
    def __init__(self):
        self.cartes = []

    def ajouter_carte(self, carte):
        self.cartes.append(carte)

    def __str__(self):
        return ', '.join(str(carte) for carte in self.cartes)

    def evaluer(self, cartes_communes):
        toutes_les_cartes = self.cartes + cartes_communes
        valeurs = [c.valeur for c in toutes_les_cartes]
        couleurs = [c.couleur for c in toutes_les_cartes]

        # Comptage des valeurs
        compteur_valeurs = Counter(valeurs)
        frequence = sorted(compteur_valeurs.items(), key=lambda item: (item[1], item[0]), reverse=True)
        valeurs_triees = sorted([self.valeur_numerique(v) for v in valeurs], reverse=True)

        is_couleur = len(set(couleurs)) == 1
        is_quinte = len(valeurs_triees) == 5 and (valeurs_triees[0] - valeurs_triees[-1] == 4)

        if is_couleur and is_quinte:
            if valeurs_triees[0] == 13:
                return "Quinte Flush Royale", valeurs_triees
            return "Quinte Flush", valeurs_triees
        if frequence[0][1] == 4:
            return "Carré", valeurs_triees
        if frequence[0][1] == 3 and frequence[1][1] == 2:
            return "Full", valeurs_triees
        if is_couleur:
            return "Couleur", valeurs_triees
        if is_quinte:
            return "Quinte", valeurs_triees
        if frequence[0][1] == 3:
            return "Brelan", valeurs_triees
        if frequence[0][1] == 2 and frequence[1][1] == 2:
            return "Double Paire", valeurs_triees
        if frequence[0][1] == 2:
            return "Paire", valeurs_triees
        return "Carte Haute", valeurs_triees

    @staticmethod
    def valeur_numerique(valeur):
        valeurs_numeriques = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'Valet': 11, 'Dame': 12, 'Roi': 13, 'As': 14
        }
        return valeurs_numeriques[valeur]

# Classe représentant un joueur
class Joueur:
    def __init__(self, nom):
        self.nom = nom
        self.main = Main()
        self.jetons = 100

    def miser(self, montant):
        if montant > self.jetons:
            montant = self.jetons
        self.jetons -= montant
        return montant

# Classe représentant la table de poker
class TableDePoker:
    def __init__(self):
        self.joueurs = []
        self.jeu_de_cartes = JeuDeCartes()
        self.pot = 0
        self.cartes_communes = []

    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)

    def debuter_partie(self):
        for joueur in self.joueurs:
            joueur.main.ajouter_carte(self.jeu_de_cartes.distribuer())
            joueur.main.ajouter_carte(self.jeu_de_cartes.distribuer())

        # Distribuer les cartes communes
        for _ in range(3):  # Flop
            self.cartes_communes.append(self.jeu_de_cartes.distribuer())
        self.cartes_communes.append(self.jeu_de_cartes.distribuer())  # Turn
        self.cartes_communes.append(self.jeu_de_cartes.distribuer())  # River

    def afficher_table(self):
        print("Cartes communes :", ', '.join(str(carte) for carte in self.cartes_communes))

    def tour_de_mise(self):
        for joueur in self.joueurs:
            if joueur.nom == "Humain":
                print(f"{joueur.nom}, vous avez {joueur.jetons} jetons.")
                action = input("Voulez-vous miser (M), suivre (S), ou se coucher (C)? ").strip().upper()
                if action == 'M':
                    montant = int(input("Combien voulez-vous miser ? "))
                    self.pot += joueur.miser(montant)
                elif action == 'S':
                    self.pot += joueur.miser(10)  # Suivre avec un montant fixe
                elif action == 'C':
                    print(f"{joueur.nom} se couche.")
                    continue
            else:
                print(f"{joueur.nom} (IA) prend une décision...")
                if joueur.jetons > 10:
                    self.pot += joueur.miser(10)  # IA suit
                    print(f"{joueur.nom} mise 10 jetons.")
                else:
                    print(f"{joueur.nom} se couche.")

    def determiner_gagnant(self):
        meilleurs_scores = {}
        for joueur in self.joueurs:
            main_score, valeurs = joueur.main.evaluer(self.cartes_communes)
            meilleurs_scores[joueur.nom] = (main_score, valeurs)

        # Déterminer le gagnant en fonction du score
        gagnant = max(meilleurs_scores, key=lambda k: (self.score_poker(meilleurs_scores[k][0]), meilleurs_scores[k][1]))
        print(f"Le gagnant est {gagnant} avec {meilleurs_scores[gagnant][0]}")

    @staticmethod
    def score_poker(score):
        valeurs_rang = {
            "Carte Haute": 1,
            "Paire": 2,
            "Double Paire": 3,
            "Brelan": 4,
            "Quinte": 5,
            "Couleur": 6,
            "Full": 7,
            "Carré": 8,
            "Quinte Flush": 9,
            "Quinte Flush Royale": 10
        }
        return valeurs_rang[score]

# Fonction principale pour exécuter le jeu
def main():
    table = TableDePoker()
    joueur_humain = Joueur("Humain")
    joueur_ia = Joueur("IA")

    table.ajouter_joueur(joueur_humain)
    table.ajouter_joueur(joueur_ia)

    table.debuter_partie()
    table.afficher_table()
    table.tour_de_mise()
    table.determiner_gagnant()

if __name__ == "__main__":
    main()
