from odoo import models, fields


class StockLot(models.Model):
    _inherit = "stock.lot"

    qm_freigabe_id = fields.Many2one(
        comodel_name="qm.freigabe",
        string="QM-Freigabe",
    )
    qm_state = fields.Selection(
        related="qm_freigabe_id.state",
        string="QM-Status",
        store=True,
    )