from odoo import models, fields, api, _
from odoo.exceptions import UserError


class QmFreigabe(models.Model):
    _name = "qm.freigabe"
    _description = "QM Chargenfreigabe"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Referenz",
        required=True,
        copy=False,
        readonly=True,
        default="Neu",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Entwurf"),
            ("pruefung", "In Prüfung"),
            ("freigegeben", "Freigegeben"),
            ("gesperrt", "Gesperrt"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    pruefdatum = fields.Date(string="Prüfdatum", tracking=True)
    bemerkung = fields.Text(string="Bemerkung")
    
    lot_ids = fields.One2many(
        comodel_name="stock.lot",
        inverse_name="qm_freigabe_id",
        string="Chargen",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Neu") == "Neu":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "qm.freigabe"
                ) or "Neu"
        return super().create(vals_list)
    
    def action_pruefung_starten(self):
        self.state = "pruefung"
        self._qm_aktivitaet_erzeugen()

    def _qm_aktivitaet_erzeugen(self):
        qm_gruppe = self.env.ref("qm_freigabe.group_qm_manager")
        for freigabe in self:
            for user in qm_gruppe.users:
                freigabe.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Chargenfreigabe prüfen"),
                    note=_("Bitte %s prüfen und freigeben.") % freigabe.name,
                    user_id=user.id,
                )       
                
    def action_freigeben(self):
        for freigabe in self:
            if not freigabe.pruefdatum:
                raise UserError("Bitte zuerst ein Prüfdatum eintragen.")
        self.state = "freigegeben"

    def action_sperren(self):
        self.state = "gesperrt"

    def action_zuruecksetzen(self):
        self.state = "draft"