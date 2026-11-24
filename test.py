from decimal import Decimal

from Cafeteria import Cafeteria
from Client import Client
from Commande import Commande
from Produit import Produit
from Profile import Profile
from Status import Status


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

recharge_test = Client("Recharge 100", 10.00, Profile.etudiant)

assert recharge_test.recharger(100.00) is True
assert recharge_test.solde == 110.00
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
commande = Commande(client, "09:00" , Status.accepter)
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
commande = Commande(alice, "09:00" , Status.accepter)
commande.ajouter_ligne(cafe, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert motif == ""
assert montant == Decimal("1.08")
assert cafe.stock == stock_avant - 1
assert alice.solde == round(solde_avant - montant, 2)

produit_inconnu = Produit("SM1", "Smoothie mangue", "boisson froide", 3.00, 0)
commande = Commande(alice, "13:00" , Status.accepter)
commande.ajouter_ligne(produit_inconnu, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is False
assert motif == "produit inconnu"
assert montant == 0.00
assert cafeteria.refus["produit inconnu"] == 1

# An order without lines is rejected and is not added to the journal.
commandes_avant = len(cafeteria.journal)
chiffre_affaires_avant = cafeteria.chiffre_affaires
commande = Commande(alice, "10:00" , Status.accepter)
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
commande = Commande(alice, "10:00" , Status.accepter)
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
commande = Commande(alice, "10:00" , Status.accepter)
commande.ajouter_ligne(cafe, 2)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert montant == Decimal("0.16")
assert alice.pointfid == 0

# Visitors pay the service fee and do not use badge loyalty.
visiteur = Client("Visiteur test", 0.00, Profile.visiteur)
commande = Commande(visiteur, "10:00" , Status.accepter)
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
commande = Commande(client_atomic, "10:00" , Status.accepter)
commande.ajouter_ligne(cafe_atomic, 1)
commande.ajouter_ligne(the_atomic, 1)
acceptee, motif, montant = cafeteria_atomic.traiter_commande(commande)
assert acceptee is False
assert motif == "transaction échouée"
assert montant == Decimal("0.00")
assert cafe_atomic.stock == stock_avant
assert the_atomic.stock == stock_the_avant
assert client_atomic.solde == solde_avant

# Cancellation tests

# 1. Cancelling the last order restores the stock, balance and fidelity.
cafe_annulation = Cafeteria()
alice_annulation = cafe_annulation.clients[0]
produit_annulation = cafe_annulation.chercher_produit("BO1")
solde_avant_annulation = alice_annulation.solde
stock_avant_annulation = produit_annulation.stock
points_avant_annulation = alice_annulation.pointfid
commande_annulation = Commande(alice_annulation, "10:00", Status.accepter)
assert commande_annulation.ajouter_ligne(produit_annulation, 1)
acceptee, _, montant_annulation = cafe_annulation.traiter_commande(
    commande_annulation
)
assert acceptee is True
annulee, motif, rembourse = cafe_annulation.annuler_commande(
    commande_annulation.numero
)
assert annulee is True
assert motif == ""
assert rembourse == montant_annulation
assert produit_annulation.stock == stock_avant_annulation
assert alice_annulation.solde == solde_avant_annulation
assert alice_annulation.pointfid == points_avant_annulation

# 2. An unknown order cannot be cancelled.
cafe_inconnue = Cafeteria()
annulee, motif, rembourse = cafe_inconnue.annuler_commande(999999)
assert annulee is False
assert motif == "commande inconnue"
assert rembourse == Decimal("0.00")

# 3. An order already cancelled cannot be cancelled twice.
cafe_double = Cafeteria()
alice_double = cafe_double.clients[0]
cafe_double_produit = cafe_double.chercher_produit("BO1")
commande_double = Commande(alice_double, "10:00", Status.accepter)
commande_double.ajouter_ligne(cafe_double_produit, 1)
assert cafe_double.traiter_commande(commande_double)[0] is True
assert cafe_double.annuler_commande(commande_double.numero)[0] is True
annulee, motif, rembourse = cafe_double.annuler_commande(
    commande_double.numero
)
assert annulee is False
assert motif == "commande déjà annulée"
assert rembourse == Decimal("0.00")

# 4. A refused cancellation changes nothing.
cafe_refus = Cafeteria()
alice_refus = cafe_refus.clients[0]
cafe_refus_produit = cafe_refus.chercher_produit("BO1")
solde_refus = alice_refus.solde
stock_refus = cafe_refus_produit.stock
points_refus = alice_refus.pointfid
annulee, motif, rembourse = cafe_refus.annuler_commande(999998)
assert annulee is False
assert motif == "commande inconnue"
assert rembourse == Decimal("0.00")
assert alice_refus.solde == solde_refus
assert cafe_refus_produit.stock == stock_refus
assert alice_refus.pointfid == points_refus

# 5. A visitor is refunded without changing its balance.
cafe_visiteur = Cafeteria()
visiteur_annulation = Client("Visiteur", 0.00, Profile.visiteur)
produit_visiteur = cafe_visiteur.chercher_produit("BO1")
commande_visiteur = Commande(visiteur_annulation, "10:00", Status.accepter)
commande_visiteur.ajouter_ligne(produit_visiteur, 1)
acceptee, _, montant_visiteur = cafe_visiteur.traiter_commande(
    commande_visiteur
)
assert acceptee is True
assert cafe_visiteur.annuler_commande(commande_visiteur.numero) == (
    True,
    "",
    montant_visiteur,
)
assert visiteur_annulation.solde == Decimal("0.00")

# 6. A badge refund bypasses the 150.00 recharge ceiling.
cafe_plafond = Cafeteria()
alice_plafond = cafe_plafond.clients[0]
alice_plafond.solde = Decimal("149.50")
cafe_plafond_produit = cafe_plafond.chercher_produit("BO1")
commande_plafond = Commande(alice_plafond, "10:00", Status.accepter)
commande_plafond.ajouter_ligne(cafe_plafond_produit, 1)
assert cafe_plafond.traiter_commande(commande_plafond)[0] is True
commande_plafond.montant_paye = Decimal("149.00")
assert cafe_plafond.annuler_commande(commande_plafond.numero)[0] is True
assert alice_plafond.solde == Decimal("297.42")

# 7. Cancelling a loyalty-reward order restores fidelity by replay.
cafe_avantage = Cafeteria()
alice_avantage = cafe_avantage.clients[0]
alice_avantage.pointfid = 30
produit_avantage = cafe_avantage.chercher_produit("BO1")
commande_avantage = Commande(alice_avantage, "10:00", Status.accepter)
commande_avantage.ajouter_ligne(produit_avantage, 2)
acceptee, _, _ = cafe_avantage.traiter_commande(commande_avantage)
assert acceptee is True
assert alice_avantage.pointfid == 0
assert cafe_avantage.annuler_commande(commande_avantage.numero)[0] is True
assert alice_avantage.pointfid == 0

# 8. A cancelled order is retained in the journal and prints as cancelled.
cafe_ticket = Cafeteria()
alice_ticket = cafe_ticket.clients[0]
produit_ticket = cafe_ticket.chercher_produit("BO1")
commande_ticket = Commande(alice_ticket, "10:00", Status.accepter)
commande_ticket.ajouter_ligne(produit_ticket, 1)
assert cafe_ticket.traiter_commande(commande_ticket)[0] is True
assert cafe_ticket.annuler_commande(commande_ticket.numero)[0] is True
assert len(cafe_ticket.journal) == 1
assert commande_ticket in cafe_ticket.journal
assert "ANNULÉE" in str(commande_ticket)

# Recall cancels every live order containing the product in chronological order
# and returns the other products while destroying the recalled stock.
cafe_rappel = Cafeteria()
bruno_rappel = cafe_rappel.clients[1]
alice_rappel = cafe_rappel.clients[0]
assert bruno_rappel.recharger(20.00) is True
wrap_rappel = cafe_rappel.chercher_produit("PO2")
eau_rappel = cafe_rappel.chercher_produit("BO5")
commande_bruno_rappel = Commande(bruno_rappel, "12:15", Status.accepter)
commande_bruno_rappel.ajouter_ligne(wrap_rappel, 2)
commande_bruno_rappel.ajouter_ligne(eau_rappel, 1)
assert cafe_rappel.traiter_commande(commande_bruno_rappel)[0] is True
commande_alice_rappel = Commande(alice_rappel, "12:20", Status.accepter)
commande_alice_rappel.ajouter_ligne(wrap_rappel, 1)
assert cafe_rappel.traiter_commande(commande_alice_rappel)[0] is True
ok, motif, resume_rappel = cafe_rappel.rappeler_produit("PO2")
assert ok is True
assert motif == ""
assert "2 commande(s)" in resume_rappel
assert commande_bruno_rappel.rappel_code == "PO2"
assert commande_alice_rappel.rappel_code == "PO2"
assert wrap_rappel.rappelle is True
assert wrap_rappel.stock == 0
assert eau_rappel.stock == 40

# A recall with no matching orders still marks and empties the product.
cafe_rappel_vide = Cafeteria()
wrap_rappel_vide = cafe_rappel_vide.chercher_produit("PO2")
ok, _, resume_vide = cafe_rappel_vide.rappeler_produit("PO2")
assert ok is True
assert "0 commande(s)" in resume_vide
assert wrap_rappel_vide.stock == 0

# Recalled products cannot be sold or replenished.
cafe_produit_rappelle = Cafeteria()
wrap_produit_rappelle = cafe_produit_rappelle.chercher_produit("PO2")
assert cafe_produit_rappelle.rappeler_produit("PO2")[0] is True
commande_produit_rappelle = Commande(
    cafe_produit_rappelle.clients[0], "12:35", Status.accepter
)
commande_produit_rappelle.ajouter_ligne(wrap_produit_rappelle, 1)
ok, motif, _ = cafe_produit_rappelle.traiter_commande(
    commande_produit_rappelle
)
assert ok is False
assert motif == "produit rappelé"
assert cafe_produit_rappelle.journal == []
assert wrap_produit_rappelle.stock == 0
assert cafe_produit_rappelle.reapprovisionner("PO2", 10) is False
assert wrap_produit_rappelle.stock == 0
assert cafe_produit_rappelle.refus["produit rappelé"] == 2

# A second recall is rejected and counted.
cafe_second_rappel = Cafeteria()
assert cafe_second_rappel.rappeler_produit("PO2")[0] is True
ok, motif, _ = cafe_second_rappel.rappeler_produit("PO2")
assert ok is False
assert motif == "déjà rappelé"
assert cafe_second_rappel.refus["déjà rappelé"] == 1

# Scenario v2
cafe_v2 = Cafeteria()
rapport_v2 = cafe_v2.scenario_v2()
wrap_v2 = cafe_v2.chercher_produit("PO2")
assert "RAPPORT DE CRISE" in rapport_v2
assert wrap_v2.stock == 0
assert cafe_v2.refus["commande déjà annulée"] == 1
assert cafe_v2.refus["commande inconnue"] == 1
assert cafe_v2.refus["produit rappelé"] == 2
assert cafe_v2.refus["déjà rappelé"] == 1
assert cafe_v2.total_remboursements == Decimal("19.72")

print("Tous les tests sont reussis.")
