from decimal import Decimal
from Client import Client
from Profile import Profile                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
from Produit import Produit
from Commande import Commande
from Status import Status



class Cafeteria:
    def __init__(self):
        self.carte = self.creer_carte()
        self.clients = self.creer_clients()
        self.journal = []
        self.refus = {
            "produit inconnu": 0,
            "quantité invalide": 0,
            "rupture de stock": 0,
            "hors créneau": 0,
            "solde insuffisant": 0,
            "transaction échouée": 0,
        }
        self.chiffre_affaires = Decimal("0.00")
        self.total_remises = Decimal("0.00")
        self.ventes = {}

    def creer_carte(self) -> list[Produit]:
        return [
            Produit("BO1", "Café expresso", "boisson chaude", 1.20, 100),
            Produit("BO2", "Thé", "boisson chaude", 1.30, 60),
            Produit("BO3", "Chocolat chaud", "boisson chaude", 1.60, 40),
            Produit("BO4", "Jus d'orange", "boisson froide", 2.00, 24),
            Produit("BO5", "Eau 50 cl", "boisson froide", 1.00, 40),
            Produit("VO1", "Croissant", "viennoiserie", 1.20, 30),
            Produit("PO1", "Sandwich jambon-beurre", "plat", 4.00, 15),
            Produit("PO2", "Wrap végétarien", "plat", 4.60, 10),
            Produit("PO3", "Plat du jour", "plat", 7.20, 20),
            Produit("DO1", "Cookie", "dessert", 1.40, 25),
            Produit("DO2", "Fruit de saison", "dessert", 0.80, 30),
        ]

    def creer_clients(self) -> list[Client]:
        return [
            Client("Alice", 12.00, Profile.etudiant),
            Client("Bruno", 3.50, Profile.alternant),
            Client("Chloé", 25.00, Profile.etudiant),
            Client("Farid", 0.00, Profile.personnel),
        ]

    def chercher_produit(self, code: str) -> Produit | None:
        for produit in self.carte:
            if produit.code == code:
                return produit
        return None

    def enregistrer_refus(self, motif: str) -> None:
        if motif in self.refus:
            self.refus[motif] += 1

    def recharger_badge(self, client: Client, montant: Decimal | float) -> bool:
        return client.recharger(montant)

    def reapprovisionner(self, code: str, quantite: int) -> bool:
        produit = self.chercher_produit(code)
        if produit is None:
            return False
        return produit.reapprovisionner(quantite)

    def ajouter_au_journal(self, commande: Commande) -> None:
        self.journal.append(commande)
        
    
    def annulation(
        self , commande: Commande
        ) -> tuple[Status , str , Decimal]:
        if not commande.lignes:
                self.enregistrer_refus("quantité invalide")
                return Status.anuller, "quantité invalide", Decimal("0.00")
        
  
        client = commande.client
        heure = commande.heure
        lignes_par_code = {}

        for produit, qte in commande.lignes:
            produit_carte = self.chercher_produit(produit.code)
            if produit_carte is None:
                self.enregistrer_refus("produit inconnu")
                return Status.anuller, "produit inconnu", Decimal("0.00")
            is_disponible, motif = produit_carte.disponible(qte, heure)
            if not is_disponible:
                if motif == "Stock n'est pas suffisant":
                    motif = "rupture de stock"
                self.enregistrer_refus(motif)
                return Status.anuller, motif, Decimal("0.00")
            if produit_carte.code in lignes_par_code:
                lignes_par_code[produit_carte.code][1] += qte
            else:
                lignes_par_code[produit_carte.code] = [produit_carte, qte]

        lignes = list(lignes_par_code.values())
        for produit, qte in lignes:
            if qte > produit.stock:
                self.enregistrer_refus("rupture de stock")
                return Status.anuller, "rupture de stock", Decimal("0.00")
        
        return Status.accepter , "" , Decimal("0.00")    
        

    def traiter_commande(
            self, commande: Commande
        ) -> tuple[bool, str, Decimal]:
            status, motif, remboursement = self.annulation(commande)
            if status == Status.anuller:
                return False, motif, remboursement

            client = commande.client
            heure = commande.heure
            lignes_par_code = {}
            
            for produit , qte in commande.lignes :
                produit_carte = self.chercher_produit(produit.code)
                lignes_par_code[produit_carte.code] = [produit_carte, qte]
            

            lignes = list(lignes_par_code.values())
            total = sum(
                (produit.prix * qte for produit, qte in lignes), Decimal("0.00")
            ).quantize(Decimal("0.01"))

            remise = Decimal("0.00")
            frais_service = Decimal("0.00")
            if client.profile == Profile.etudiant:
                remise = total * Decimal("0.10")
            elif client.profile == Profile.alternant:
                remise = total * Decimal("0.05")
            elif client.profile == Profile.visiteur:
                frais_service = Decimal("0.50")

            avantage = client.avantage_fidelite()

            montant = (total - remise - avantage + frais_service).quantize(
                Decimal("0.01")
            )

            if not client.peut_payer(montant):
                self.enregistrer_refus("solde insuffisant")
                return False, "solde insuffisant", Decimal("0.00")

            solde_avant = client.solde
            stocks_avant = {produit.code: produit.stock for produit, _ in lignes}
            if not client.debiter(montant):
                client.solde = solde_avant
                self.enregistrer_refus("transaction échouée")
                return False, "transaction échouée", Decimal("0.00")

            for produit, qte in lignes:
                if not produit.vendre(qte, heure):
                    client.solde = solde_avant
                    for produit_a_restaurer, _ in lignes:
                        produit_a_restaurer.stock = stocks_avant[produit_a_restaurer.code]
                    self.enregistrer_refus("transaction échouée")
                    return False, "transaction échouée", Decimal("0.00")

            if avantage > 0:
                client.utiliser_avantage_fidelite()

            client.ajouter_points(montant)
            self.ajouter_au_journal(commande)
            self.chiffre_affaires += montant
            self.total_remises += remise + avantage

            for produit, qte in lignes:
                self.ventes[produit.code] = self.ventes.get(produit.code, 0) + qte

            return True, "", montant

    def rapport_cloture(self) -> str:
        lignes = [
            "RAPPORT DE CLOTURE",
            f"Commandes acceptees : {len(self.journal)}",
            f"Chiffre d'affaires : {self.chiffre_affaires:.2f} EUR",
            f"Remises et avantages : {self.total_remises:.2f} EUR",
            "Refus :",
        ]

        for motif, nombre in self.refus.items():
            lignes.append(f"- {motif} : {nombre}")

        produits_vendus = []
        for code, quantite in self.ventes.items():
            produit = self.chercher_produit(code)
            produits_vendus.append((quantite, produit))

        produits_vendus.sort(reverse=True)
        lignes.append("Top 3 des ventes :")
        for quantite, produit in produits_vendus[:3]:
            lignes.append(f"- {produit.nom} : {quantite}")

        lignes.append("Carte :")
        for produit in sorted(self.carte):
            stock = f"{produit.stock}"
            if produit.stock == 0:
                stock += " (epuise)"
            lignes.append(f"- {produit.code} - {produit.nom} : {stock}")

        lignes.append("Badges avec un solde inferieur a 3.00 EUR :")
        for client in self.clients:
            if client.paiment.value == "badge" and client.solde < 3.00:
                lignes.append(f"- {client.nom} : {client.solde:.2f} EUR")

        return "\n".join(lignes)

    def sauvegarder_sortie(
        self, rapport: str, nom_fichier: str = "sortie_scenario.txt"
    ) -> None:
        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            fichier.write(rapport)

    def scenario(self):
        cafe_expresso = self.chercher_produit("BO1")
        the = self.chercher_produit("BO2")
        chocolat_chaud = self.chercher_produit("BO3")
        jus_orange = self.chercher_produit("BO4")
        eau_50cl = self.chercher_produit("BO5")
        croissant = self.chercher_produit("VO1")
        sandwich = self.chercher_produit("PO1")
        wrap = self.chercher_produit("PO2")
        plat_du_jour = self.chercher_produit("PO3")
        cookie = self.chercher_produit("DO1")
        fruit = self.chercher_produit("DO2")

        alice = self.clients[0]
        bruno = self.clients[1]
        chloe = self.clients[2]
        farid = self.clients[3]

        commande = Commande(alice, "07:45" , Status.accepter)
        commande.ajouter_ligne(cafe_expresso, 1)
        commande.ajouter_ligne(croissant, 1)
        self.traiter_commande(commande)

        commande = Commande(farid, "08:10",  Status.accepter)
        commande.ajouter_ligne(cafe_expresso, 2)
        self.traiter_commande(commande)

        commande = Commande(bruno, "08:30" ,  Status.accepter)
        commande.ajouter_ligne(chocolat_chaud, 1)
        commande.ajouter_ligne(croissant, 3)
        self.traiter_commande(commande)

        self.recharger_badge(bruno, 20.00)

        commande = Commande(bruno, "08:40",  Status.accepter)
        commande.ajouter_ligne(chocolat_chaud, 1)
        commande.ajouter_ligne(croissant, 3)
        self.traiter_commande(commande)

        visiteur = Client("Visiteur", 0.00, Profile.visiteur ,  Status.accepter)
        commande = Commande(visiteur, "09:15" , Status.accepter)
        commande.ajouter_ligne(the, 1)
        commande.ajouter_ligne(cookie, 1)
        self.traiter_commande(commande)

        commande = Commande(chloe, "11:00" ,  Status.accepter)
        commande.ajouter_ligne(plat_du_jour, 1)
        self.traiter_commande(commande)

        commande = Commande(chloe, "12:05" ,  Status.accepter)
        commande.ajouter_ligne(plat_du_jour, 1)
        commande.ajouter_ligne(jus_orange, 1)
        commande.ajouter_ligne(cookie, 1)
        self.traiter_commande(commande)

        self.recharger_badge(alice, 150.00)

        commande = Commande(alice, "12:20" , Status.accepter)
        commande.ajouter_ligne(wrap, 1)
        commande.ajouter_ligne(eau_50cl, 1)
        commande.ajouter_ligne(fruit, 1)
        commande.ajouter_ligne(cafe_expresso, 1)
        self.traiter_commande(commande)

        commande = Commande(visiteur, "12:45" , Status.accepter)
        commande.ajouter_ligne(sandwich, 16)
        self.traiter_commande(commande)

        smoothie_mangue = Produit(
            "SM1", "Smoothie mangue", "boisson froide", 3.00, 0
        )
        commande = Commande(bruno, "13:00",Status.accepter)
        commande.ajouter_ligne(sandwich, 1)
        commande.ajouter_ligne(smoothie_mangue, 1)
        self.traiter_commande(commande)

        commande = Commande(alice, "15:30",Status.accepter)
        commande.ajouter_ligne(cafe_expresso, 1)
        commande.ajouter_ligne(cookie, 1)
        self.traiter_commande(commande)

        self.reapprovisionner("PO1", 10)

        commande = Commande(farid, "17:30", Status.accepter)
        commande.ajouter_ligne(the, 2)
        self.traiter_commande(commande)

        rapport = self.rapport_cloture()
        self.sauvegarder_sortie(rapport)
        return rapport


if __name__ == "__main__":
    cafeteria = Cafeteria()
    print(cafeteria.scenario())