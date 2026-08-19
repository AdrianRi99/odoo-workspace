from odoo import models, fields, _

class StockLot(models.Model):
    _inherit = "stock.lot"

    anzahl_betroffene_produkte = fields.Integer(
        string="Betroffene Produkt-Chargen",
        compute="_compute_rueckverfolgung_counts",
    )
    anzahl_verwendete_rohstoffe = fields.Integer(
        string="Verwendete Rohstoff-Chargen",
        compute="_compute_rueckverfolgung_counts",
    )

    def _compute_rueckverfolgung_counts(self):
        Rueck = self.env["qm.rueckverfolgung"]
        for lot in self:
            # Diese Charge als Rohstoff -> welche Produkt-Chargen?
            lot.anzahl_betroffene_produkte = Rueck.search_count([
                ("rohstoff_lot_id", "=", lot.id)
            ])
            # Diese Charge als Produkt -> welche Rohstoff-Chargen?
            lot.anzahl_verwendete_rohstoffe = Rueck.search_count([
                ("produkt_lot_id", "=", lot.id)
            ])

    def action_zeige_betroffene_produkte(self):
        self.ensure_one()
        eintraege = self.env["qm.rueckverfolgung"].search([
            ("rohstoff_lot_id", "=", self.id)
        ])
        produkt_lot_ids = eintraege.mapped("produkt_lot_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": _("Betroffene Produkt-Chargen"),
            "res_model": "stock.lot",
            "view_mode": "tree,form",
            "domain": [("id", "in", produkt_lot_ids)],
        }

    def action_zeige_rohstoffe(self):
        self.ensure_one()
        eintraege = self.env["qm.rueckverfolgung"].search([
            ("produkt_lot_id", "=", self.id)
        ])
        rohstoff_lot_ids = eintraege.mapped("rohstoff_lot_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": _("Verwendete Rohstoff-Chargen"),
            "res_model": "stock.lot",
            "view_mode": "tree,form",
            "domain": [("id", "in", rohstoff_lot_ids)],
        }