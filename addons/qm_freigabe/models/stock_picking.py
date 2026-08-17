from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self._qm_pruefe_freigabe()
        return super().button_validate()

    def _qm_pruefe_freigabe(self):
        sperrmodus = self.env["ir.config_parameter"].sudo().get_param(
            "qm_freigabe.sperrmodus", default="warnen"
        )
        for picking in self:
            if picking.picking_type_id.code != "outgoing":
                continue
            gesperrte_lots = picking.move_line_ids.lot_id.filtered(
                lambda lot: lot.qm_state != "freigegeben"
            )
            if gesperrte_lots:
                namen = ", ".join(gesperrte_lots.mapped("name"))
                if sperrmodus == "blockieren":
                    raise UserError(
                        _("Auslieferung blockiert. Nicht freigegebene Chargen: %s")
                        % namen
                    )
                else:
                    picking.message_post(
                        body=_("Warnung: nicht freigegebene Chargen: %s") % namen
                    )