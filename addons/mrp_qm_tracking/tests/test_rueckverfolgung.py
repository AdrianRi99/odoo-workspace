from odoo.tests.common import TransactionCase


class TestRueckverfolgung(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Lot = self.env["stock.lot"]
        self.Rueck = self.env["qm.rueckverfolgung"]

        # Ein Rohstoff-Produkt und ein Fertigprodukt
        self.rohstoff = self.env["product.product"].create({
            "name": "Testrohstoff",
            "tracking": "lot",
        })
        self.fertigprodukt = self.env["product.product"].create({
            "name": "Testprodukt",
            "tracking": "lot",
        })

        # Chargen
        self.rohstoff_lot = self.Lot.create({
            "name": "ROH-001",
            "product_id": self.rohstoff.id,
        })
        self.produkt_lot_a = self.Lot.create({
            "name": "PROD-A",
            "product_id": self.fertigprodukt.id,
        })
        self.produkt_lot_b = self.Lot.create({
            "name": "PROD-B",
            "product_id": self.fertigprodukt.id,
        })

    def test_rohstoff_in_mehreren_produkten(self):
        # Derselbe Rohstoff floss in zwei Produkt-Chargen
        self.Rueck.create({
            "produkt_lot_id": self.produkt_lot_a.id,
            "rohstoff_lot_id": self.rohstoff_lot.id,
            "production_id": self._dummy_production().id,
        })
        self.Rueck.create({
            "produkt_lot_id": self.produkt_lot_b.id,
            "rohstoff_lot_id": self.rohstoff_lot.id,
            "production_id": self._dummy_production().id,
        })
        # Der Zähler an der Rohstoff-Charge muss 2 sein
        self.assertEqual(self.rohstoff_lot.anzahl_betroffene_produkte, 2)

    def test_rueckruf_action_findet_richtige_produkte(self):
        prod = self._dummy_production()
        self.Rueck.create({
            "produkt_lot_id": self.produkt_lot_a.id,
            "rohstoff_lot_id": self.rohstoff_lot.id,
            "production_id": prod.id,
        })
        action = self.rohstoff_lot.action_zeige_betroffene_produkte()
        # Die Action-Domain muss genau Produkt-Charge A enthalten
        domain = action["domain"]
        betroffene_ids = domain[0][2]
        self.assertIn(self.produkt_lot_a.id, betroffene_ids)
        self.assertNotIn(self.produkt_lot_b.id, betroffene_ids)

    def _dummy_production(self):
        return self.env["mrp.production"].create({
            "product_id": self.fertigprodukt.id,
        })