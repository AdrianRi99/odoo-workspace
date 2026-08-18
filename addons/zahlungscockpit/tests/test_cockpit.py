from odoo.tests.common import TransactionCase


class TestZahlungscockpit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Partner = self.env["res.partner"]
        self.partner = self.Partner.create({"name": "Testfirma"})

    def test_score_perfekt(self):
        # Kein Verzug, keine Überfälligen -> voller Score
        score = self.partner._berechne_score(0.0, 0)
        self.assertEqual(score, 100)

    def test_score_mit_verzug(self):
        # 5 Tage Ø-Verzug -> 15 Punkte Abzug
        score = self.partner._berechne_score(5.0, 0)
        self.assertEqual(score, 85)

    def test_score_untergrenze(self):
        # Extremwerte dürfen nicht unter 0 fallen
        score = self.partner._berechne_score(100.0, 20)
        self.assertEqual(score, 0)

    def test_bewertung_schwellen(self):
        self.assertEqual(self.partner._score_zu_bewertung(90), "gut")
        self.assertEqual(self.partner._score_zu_bewertung(60), "mittel")
        self.assertEqual(self.partner._score_zu_bewertung(30), "schlecht")

    def test_warnungs_grund_leer_bei_gutem_partner(self):
        # Guter Partner (hoher Score, kein Skonto verpasst) -> kein Grund
        self.partner.zuverlaessigkeit_score = 90
        self.partner.skonto_verpasst_summe = 0.0
        grund = self.partner._warnungs_grund(50, 100.0)
        self.assertEqual(grund, "")