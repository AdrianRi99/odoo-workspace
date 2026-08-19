from odoo import models, fields


class QmRueckverfolgung(models.Model):
    _name = "qm.rueckverfolgung"
    _description = "Chargen-Rückverfolgung"
    _order = "create_date desc"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Fertigungsauftrag",
        required=True,
        ondelete="cascade",
        index=True,
    )
    produkt_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Produkt-Charge",
        required=True,
        index=True,
    )
    rohstoff_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Rohstoff-Charge",
        required=True,
        index=True,
    )
    rohstoff_produkt_id = fields.Many2one(
        comodel_name="product.product",
        string="Rohstoff",
        related="rohstoff_lot_id.product_id",
        store=True,
    )
    datum = fields.Datetime(
        string="Erfasst am",
        default=fields.Datetime.now,
    )