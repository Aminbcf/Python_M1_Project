**Date : 14 novembre 2026**

- J'ai terminé les quatre classes et le scénario.
- J'ai choisi la variante A1/B1.
- J'ai ajouté des assertions simples dans `test.py`.
- Le rapport est enregistré dans `sortie_scenario.txt`.
- J'ai gardé la lettre `O` dans les codes produits, comme dans mon programme.

**Presentation day :**

Phase 1 :

* je vois que j'ai deja implmentez une annulation je dois la adaptedz au status

- J'ai ajouté le status aux commandes.
- J'ai adapté l'annulation pour utiliser le status.
- L'annulation remet le stock et rembourse le client.
- J'ai ajouté les tests pour vérifier les annulations et les commandes déjà annulées.
- J'ai ajouté le scénario v2 dans `Cafeteria.py`.
- J'ai ajouté les commandes, les annulations et les rappels du Wrap à 12:30 et 12:40.
- J'ai ajouté le rapport de crise à 18:30.
- J'ai ajouté des assertions pour vérifier le stock final, les annulations et les remboursements.
- Calcul à la main de l’événement 12:18 (achat du Wrap par Chloé) et de l’annulation à 12:25 du scénario v2.
- 12:18 : montant payé **4,14 EUR**, solde avant **15,46 EUR**, solde après **11,32 EUR**, fidélité avant **9 points**, fidélité après **13 points**.
- 12:25 : remboursement **4,14 EUR**, solde avant **11,32 EUR**, solde après **15,46 EUR**, fidélité avant **13 points**, fidélité après **9 points**.
- Comparaison avec `Cafeteria.py` : aucun écart observé. Le programme et le calcul manuel avaient raison.

Phase 2 :

- J'ai ajouté le rappel d'un produit : le stock est détruit, les ventes sont bloquées et les réapprovisionnements sont refusés.
- Le rappel annule dans l'ordre les commandes encore acceptées, rembourse les clients et conserve le détail des clients touchés.
- J'ai ajouté les tests du rappel, des refus de vente et de réapprovisionnement, et du second rappel.
- Calcul du rappel à 12:30 : le rappel annule les commandes encore actives de Bruno et Alice, pour **8,74 EUR** et **6,84 EUR**. Avec les **4,14 EUR** remboursés à Chloé à 12:25, le total remboursé est **19,72 EUR**.

Phase 3 :

- J'ai mis à jour le rapport de clôture pour ignorer les commandes annulées dans les ventes, les remises et le chiffre d'affaires.
- Le rapport indique les annulations dues au rappel, le total remboursé et les clients de chaque rappel, triés par montant.
- J'ai ajouté la section « Évolution v2.0 » au README et enregistré la sortie du scénario dans `sortie_scenario_v2.txt`.
