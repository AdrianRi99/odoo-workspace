from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cockpit_score_schwelle = fields.Integer(
        string="Score-Schwelle für Warnung",
        default=50,
        config_parameter="zahlungscockpit.score_schwelle",
    )
    cockpit_skonto_schwelle = fields.Float(
        string="Skonto-Warnschwelle (€)",
        default=100.0,
        config_parameter="zahlungscockpit.skonto_schwelle",
    )