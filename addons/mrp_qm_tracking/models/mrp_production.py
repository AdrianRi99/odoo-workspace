from odoo import models, fields, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    hat_gesperrte_rohstoffe = fields.Boolean(
        string="Gesperrte Rohstoffe",
        compute="_compute_gesperrte_rohstoffe",
    )

    def _compute_gesperrte_rohstoffe(self):
        for production in self:
            gesperrte = production._finde_gesperrte_rohstoff_lots()
            production.hat_gesperrte_rohstoffe = bool(gesperrte)

    def _finde_gesperrte_rohstoff_lots(self):
        self.ensure_one()
        # move_raw_ids = die Rohstoff-Bewegungen (Verbrauch) dieser Produktion
        rohstoff_lots = self.move_raw_ids.move_line_ids.lot_id
        return rohstoff_lots.filtered(
            lambda lot: lot.qm_freigabe_id and lot.qm_state != "freigegeben"
        )

    def button_mark_done(self):
        for production in self:
            gesperrte = production._finde_gesperrte_rohstoff_lots()
            if gesperrte:
                namen = ", ".join(gesperrte.mapped("name"))
                raise UserError(
                    _("Produktion mit gesperrten Rohstoff-Chargen nicht "
                      "möglich: %s") % namen
                )
        res = super().button_mark_done()
        for production in self:
            production._erzeuge_qm_freigabe_fuer_produkt()
            production._erzeuge_rueckverfolgung()
        return res

    def _erzeuge_qm_freigabe_fuer_produkt(self):
        self.ensure_one()
        # Die erzeugten Fertigprodukt-Chargen dieser Produktion
        produkt_lots = self.move_finished_ids.filtered(
            lambda m: m.state == "done" and m.product_id == self.product_id
        ).move_line_ids.lot_id
        for lot in produkt_lots:
            if lot.qm_freigabe_id:
                continue  # schon eine Freigabe dran
            freigabe = self.env["qm.freigabe"].create({
                "bemerkung": _("Automatisch erzeugt aus Fertigung %s")
                             % self.name,
            })
            lot.qm_freigabe_id = freigabe.id
            
    erzeugte_freigabe_ids = fields.Many2many(
        comodel_name="qm.freigabe",
        string="Erzeugte QM-Freigaben",
        compute="_compute_erzeugte_freigaben",
    )

    def _compute_erzeugte_freigaben(self):
        for production in self:
            lots = production.move_finished_ids.move_line_ids.lot_id
            production.erzeugte_freigabe_ids = lots.mapped("qm_freigabe_id")
            
    def _erzeuge_rueckverfolgung(self):
        self.ensure_one()
        produkt_lots = self.move_finished_ids.filtered(
            lambda m: m.state == "done" and m.product_id == self.product_id
        ).move_line_ids.lot_id
        rohstoff_lots = self.move_raw_ids.move_line_ids.lot_id

        Rueckverfolgung = self.env["qm.rueckverfolgung"]
        for produkt_lot in produkt_lots:
            for rohstoff_lot in rohstoff_lots:
                # Doppelte vermeiden
                vorhanden = Rueckverfolgung.search_count([
                    ("production_id", "=", self.id),
                    ("produkt_lot_id", "=", produkt_lot.id),
                    ("rohstoff_lot_id", "=", rohstoff_lot.id),
                ])
                if not vorhanden:
                    Rueckverfolgung.create({
                        "production_id": self.id,
                        "produkt_lot_id": produkt_lot.id,
                        "rohstoff_lot_id": rohstoff_lot.id,
                    })