from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestQmFreigabe(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Freigabe = self.env["qm.freigabe"]
        self.freigabe = self.Freigabe.create({})

    def test_referenz_wird_vergeben(self):
        self.assertNotEqual(
            self.freigabe.name, "Neu",
            "Die Referenz sollte automatisch gesetzt werden.",
        )
        self.assertTrue(self.freigabe.name.startswith("QM/"))

    def test_freigabe_ohne_pruefdatum_scheitert(self):
        self.freigabe.action_pruefung_starten()
        with self.assertRaises(UserError):
            self.freigabe.action_freigeben()

    def test_freigabe_mit_pruefdatum_klappt(self):
        self.freigabe.action_pruefung_starten()
        self.freigabe.pruefdatum = "2026-01-01"
        self.freigabe.action_freigeben()
        self.assertEqual(self.freigabe.state, "freigegeben")

    def test_workflow_reihenfolge(self):
        self.assertEqual(self.freigabe.state, "draft")
        self.freigabe.action_pruefung_starten()
        self.assertEqual(self.freigabe.state, "pruefung")