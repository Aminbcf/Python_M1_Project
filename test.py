from decimal import Decimal

from Cafeteria import Cafeteria
from Client import Client
from Commande import Commande
from Produit import Produit
from Profile import Profile


# Produit
produit = Produit("BO1", "Café expresso", "boisson chaude", 1.20, 2)
assert produit.code == "BO1"
assert produit.prix == Decimal("1.20")
assert produit.stock == 2
assert produit.disponible(1, "10:00")[0] is True
assert produit.disponible(0, "10:00")[0] is False
assert produit.disponible(3, "10:00")[0] is False
plat = Produit("PO1", "Sandwich", "plat", 4.00, 1)
assert plat.disponible(1, "11:30")[0] is True
assert plat.disponible(1, "14:00")[0] is False
assert plat.vendre(1, "11:30") is True
assert plat.stock == 0
assert plat.reapprovisionner(2) is True
assert plat.stock == 2
assert Produit("BO1", "Autre nom", "autre", 9.00, 1) == produit

# Client
client = Client("Test", 10.00, Profile.etudiant)
assert client.recharger(5.00) is True
assert client.solde == 15.00
assert client.recharger(4.99) is False
assert client.recharger(101.00) is False
assert client.peut_payer(15.00) is True
assert client.peut_payer(15.01) is False
assert client.debiter(5.00) is True
assert client.solde == 10.00
personnel = Client("Personnel", 0.00, Profile.personnel)
assert personnel.peut_payer(10.00) is True
assert personnel.peut_payer(10.01) is False
visiteur = Client("Visiteur", 0.00, Profile.visiteur)
assert visiteur.recharger(20.00) is False
assert visiteur.avantage_fidelite() == Decimal("0.00")

# Commande
commande = Commande(client, "09:00")
assert commande.ajouter_ligne(produit, 2) is True
assert len(commande) == 2
assert produit in commande
assert commande.total() == Decimal("2.40")
assert list(commande) == [(produit, 2)]

# Cafeteria and the O product codes
cafeteria = Cafeteria()
assert cafeteria.chercher_produit("BO1") is not None
assert cafeteria.chercher_produit("B01") is None
alice = cafeteria.clients[0]
cafe = cafeteria.chercher_produit("BO1")
stock_avant = cafe.stock
solde_avant = alice.solde
commande = Commande(alice, "09:00")
commande.ajouter_ligne(cafe, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert motif == ""
assert montant == Decimal("1.08")
assert cafe.stock == stock_avant - 1
assert alice.solde == round(solde_avant - montant, 2)

produit_inconnu = Produit("SM1", "Smoothie mangue", "boisson froide", 3.00, 0)
commande = Commande(alice, "13:00")
commande.ajouter_ligne(produit_inconnu, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is False
assert motif == "produit inconnu"
assert montant == 0.00
assert cafeteria.refus["produit inconnu"] == 1

# An order without lines is rejected and is not added to the journal.
commandes_avant = len(cafeteria.journal)
chiffre_affaires_avant = cafeteria.chiffre_affaires
commande = Commande(alice, "10:00")
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is False
assert motif == "quantité invalide"
assert montant == 0.00
assert len(cafeteria.journal) == commandes_avant
assert cafeteria.chiffre_affaires == chiffre_affaires_avant
assert cafeteria.refus["quantité invalide"] == 1

# A command is validated against the card product and against its aggregated stock.
cafe = cafeteria.chercher_produit("BO1")
stock_avant = cafe.stock
solde_avant = alice.solde
produit_substitut = Produit("BO1", "Café premium", "boisson chaude", 99.00, 100)
commande = Commande(alice, "10:00")
commande.ajouter_ligne(produit_substitut, 1)
commande.ajouter_ligne(produit_substitut, stock_avant)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is False
assert motif == "rupture de stock"
assert montant == 0.00
assert cafe.stock == stock_avant
assert alice.solde == solde_avant

# Loyalty redemption is applied once.
alice.pointfid = 30
commande = Commande(alice, "10:00")
commande.ajouter_ligne(cafe, 2)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert montant == Decimal("0.16")
assert alice.pointfid == 0

# Visitors pay the service fee and do not use badge loyalty.
visiteur = Client("Visiteur test", 0.00, Profile.visiteur)
commande = Commande(visiteur, "10:00")
commande.ajouter_ligne(cafe, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert montant == Decimal("1.70")
assert visiteur.pointfid == 0

# Plat availability includes the start time and excludes the end time.
plat = cafeteria.chercher_produit("PO1")
for heure, disponible in (("11:29", False), ("11:30", True), ("14:00", False)):
    assert plat.disponible(1, heure)[0] is disponible

# A failed stock mutation rolls back the debit and every stock mutation.
cafeteria_atomic = Cafeteria()
client_atomic = cafeteria_atomic.clients[0]
cafe_atomic = cafeteria_atomic.chercher_produit("BO1")
the_atomic = cafeteria_atomic.chercher_produit("BO2")
stock_avant = cafe_atomic.stock
stock_the_avant = the_atomic.stock
solde_avant = client_atomic.solde
the_atomic.vendre = lambda quantite, heure: False
commande = Commande(client_atomic, "10:00")
commande.ajouter_ligne(cafe_atomic, 1)
commande.ajouter_ligne(the_atomic, 1)
acceptee, motif, montant = cafeteria_atomic.traiter_commande(commande)
assert acceptee is False
assert motif == "transaction échouée"
assert montant == Decimal("0.00")
assert cafe_atomic.stock == stock_avant
assert the_atomic.stock == stock_the_avant
assert client_atomic.solde == solde_avant

print("Tous les tests sont reussis.")
