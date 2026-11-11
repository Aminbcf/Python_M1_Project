from Client import Client
from Profile import Profile
from Produit import Produit
from Commande import Commande



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
        }
        self.chiffre_affaires = 0.00
        self.total_remises = 0.00
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

    def recharger_badge(self, client: Client, montant: float) -> bool:
        return client.recharger(montant)

    def reapprovisionner(self, code: str, quantite: int) -> bool:
        produit = self.chercher_produit(code)
        if produit is None:
            return False
        return produit.reapprovisionner(quantite)

    def ajouter_au_journal(self, commande: Commande) -> None:
        self.journal.append(commande)

    def traiter_commande(
        self, commande: Commande
    ) -> tuple[bool, str, float]:
        client = commande.client
        heure = commande.heure

        for produit, qte in commande.lignes:
            is_disponible, motif = produit.disponible(qte, heure)
            if not is_disponible:
                if motif == "Stock n'est pas suffisant":
                    motif = "rupture de stock"
                self.enregistrer_refus(motif)
                return False, motif, 0.00

        total = commande.total()

        remise = 0.00
        frais_service = 0.00
        if client.profile == Profile.etudiant:
            remise = total * 0.10
        elif client.profile == Profile.alternant:
            remise = total * 0.05
        elif client.profile == Profile.visiteur:
            frais_service = 0.50

        avantage = client.avantage_fidelite()

        montant = round(total - remise - avantage + frais_service, 2)

        if not client.peut_payer(montant):
            self.enregistrer_refus("solde insuffisant")
            return False, "solde insuffisant", 0.00

        client.debiter(montant)

        for produit, qte in commande.lignes:
            produit.vendre(qte, heure)

        if avantage > 0:
            client.utiliser_avantage_fidelite()

        client.ajouter_points(montant)
        self.ajouter_au_journal(commande)
        self.chiffre_affaires += montant
        self.total_remises += remise + avantage

        for produit, qte in commande.lignes:
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

    def scenario(self):
        cafe_expresso = Produit("BO1","Café expresso","boisson chaude",1.20,100)
        the = Produit("B02", "Thé", "boisson chaude", 1.30, 60)
        chocolat_chaud = Produit("B03", "Chocolat chaud", "boisson chaude", 1.60, 40)
        jus_orange = Produit("B04", "Jus d'orange", "boisson froide", 2.00, 24)
        eau_50cl = Produit("B05", "Eau 50 cl", "boisson froide", 1.00, 40)
        croissant = Produit("V01", "Croissant", "viennoiserie", 1.20, 30)
        sandwich_jambon_beurre = Produit("P01", "Sandwich jambon-beurre", "plat", 4.00, 15)
        wrap_vegetarien = Produit("P02", "Wrap végétarien", "plat", 4.60, 10)
        plat_du_jour = Produit("P03", "Plat du jour", "plat", 7.20, 20)
        cookie = Produit("D01", "Cookie", "dessert", 1.40, 25)
        fruit_saison = Produit("D02", "Fruit de saison", "dessert", 0.80, 30)
        
        alice = Client("Alice" , 12.00 ,Profile.etudiant)
        bruno = Client("Bruno" , 3.50 , Profile.alternant)
        chloe = Client("Chloé" , 25.00 , Profile.etudiant)
        farid = Client("Farid" , 0.00 , Profile.personnel)
        
        
        cmd1 = Commande(alice , "07:30")
        cmd1.ajouter_ligne(cafe_expresso,1)
        cmd1.ajouter_ligne(croissant,1)
        
        
        
                

Wenov = Cafeteria()

Wenov.scenario() 
                
        
    
    