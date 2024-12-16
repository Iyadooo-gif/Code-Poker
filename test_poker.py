import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock, call
from io import StringIO
import sys
import random
from projetpokerfinal import Carte, Joueur, Croupier, Partie, PokerApp  # Assuming your classes are in main.py

# Test de la classe Carte
class TestCarte(unittest.TestCase):

    def test_initialisation(self):
        carte = Carte('A', '♠')
        self.assertEqual(carte.rang, 'A')
        self.assertEqual(carte.couleur, '♠')
        self.assertEqual(str(carte), 'A♠')

# Test de la classe Joueur
class TestJoueur(unittest.TestCase):

    def test_initialisation(self):
        joueur = Joueur("Test")
        self.assertEqual(joueur.nom, "Test")
        self.assertEqual(joueur.tapis, 100)
        self.assertTrue(joueur.actif)

    def test_recevoir_cartes(self):
        joueur = Joueur("Test")
        carte1 = Carte('A', '♠')
        carte2 = Carte('K', '♥')
        joueur.recevoir([carte1, carte2])
        self.assertIn(carte1, joueur.cartes)
        self.assertIn(carte2, joueur.cartes)

    def test_miser(self):
        joueur = Joueur("Test", ia=False)
        mise = joueur.miser(50)
        self.assertEqual(mise, 50)
        self.assertEqual(joueur.tapis, 50)

# Test de la classe Croupier
class TestCroupier(unittest.TestCase):

    def setUp(self):
        self.croupier = Croupier()

    def test_rassembler(self):
        self.croupier.rassembler()
        self.assertEqual(len(self.croupier.paquet), 52)

    def test_melanger(self):
        self.croupier.rassembler()
        first_card = self.croupier.paquet[0]
        self.croupier.melanger()
        self.assertNotEqual(self.croupier.paquet[0], first_card)

    def test_distribuer(self):
        joueurs = [Joueur("Test1"), Joueur("Test2")]
        self.croupier.rassembler()
        self.croupier.distribuer(2, joueurs)
        self.assertEqual(len(joueurs[0].cartes), 2)
        self.assertEqual(len(joueurs[1].cartes), 2)

# Test de la classe Partie
class TestPartie(unittest.TestCase):

    def setUp(self):
        self.joueur_humain = Joueur("Vous")
        self.joueur_ia = Joueur("IA", ia=True)
        self.partie = Partie(self.joueur_humain, self.joueur_ia)
        self.partie.croupier.rassembler()
        self.partie.croupier.melanger()
        self.partie.croupier.couper()

    def test_nouvelle_partie(self):
        self.partie.nouvelle_partie()
        self.assertEqual(len(self.joueur_humain.cartes), 0)
        self.assertEqual(len(self.joueur_ia.cartes), 0)
        self.assertEqual(len(self.partie.cartes_communes), 0)
        self.assertEqual(self.partie.pot, 0)

    def test_flop(self):
        self.partie.nouvelle_partie()
        self.partie.flop()
        self.assertEqual(len(self.partie.cartes_communes), 3)

    def test_turn_or_river(self):
        self.partie.nouvelle_partie()
        self.partie.turn_or_river()
        self.assertEqual(len(self.partie.cartes_communes), 1)

    def test_ajouter_au_pot(self):
        self.partie.ajouter_au_pot(50)
        self.assertEqual(self.partie.pot, 50)

    def test_evaluer_combinaisons(self):
        scores = self.partie.evaluer_combinaisons()
        self.assertIn(self.joueur_humain, scores)
        self.assertIn(self.joueur_ia, scores)
        self.assertIsInstance(scores[self.joueur_humain], int)
        self.assertIsInstance(scores[self.joueur_ia], int)

# Test de la classe PokerApp (en mode non graphique)
class TestPokerApp(unittest.TestCase):

    def setUp(self):
        self.root = MagicMock(spec=tk.Tk)
        self.app = PokerApp(self.root)

    @patch('builtins.input', return_value='10')
    @patch('tkinter.simpledialog.askinteger', return_value=10)
    def test_miser(self, mock_input, mock_askinteger):
        self.app.partie.nouvelle_partie()
        self.app.partie.distribuer_cartes()
        self.app.miser()
        self.assertEqual(self.app.joueur_humain.tapis, 90)
        self.assertTrue(self.app.bouton_miser['state'], tk.NORMAL)

    def test_suivre(self):
        self.app.partie.nouvelle_partie()
        self.app.partie.distribuer_cartes()
        self.app.partie.ajouter_au_pot(20)  # Prépare la mise
        self.app.suivre()
        self.assertEqual(self.app.joueur_humain.tapis, 90)
        self.assertEqual(self.app.partie.pot, 30)

    def test_coucher(self):
        self.app.partie.nouvelle_partie()
        self.app.coucher()
        self.assertFalse(self.app.joueur_humain.actif)

    def test_afficher_cartes(self):
        joueur = Joueur("Test")
        joueur.recevoir([Carte('A', '♠'), Carte('K', '♥')])
        self.app.afficher_cartes(joueur, 100, 100, face_cachee=False)
        calls = [
            call.create_text(100 + 30, 100 + 45, text='A\n♠', font=("Arial", 10)),
            call.create_text(170 + 30, 100 + 45, text='K\n♥', font=("Arial", 10)),
        ]
        self.app.canvas.method_calls = []
        self.app.afficher_cartes(joueur, 100, 100, face_cachee=False)
        self.assertEqual(self.app.canvas.method_calls, calls)

if __name__ == '__main__':
    unittest.main()
