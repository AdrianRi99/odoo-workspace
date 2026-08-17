from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    qm_sperrmodus = fields.Selection(
        selection=[
            ("warnen", "Nur warnen"),
            ("blockieren", "Hart blockieren"),
        ],
        string="QM-Sperrmodus",
        default="warnen",
        config_parameter="qm_freigabe.sperrmodus",
    )