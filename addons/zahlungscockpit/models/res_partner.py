from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    durchschnitt_verzug = fields.Float(
        string="Ø Zahlungsverzug (Tage)",
        compute="_compute_zahlungskennzahlen",
        store=True,
        help="Durchschnittlicher Verzug über alle bezahlten Rechnungen.",
    )
    anzahl_ueberfaellig = fields.Integer(
        string="Überfällige Rechnungen",
        compute="_compute_zahlungskennzahlen",
        store=True,
    )
    zuverlaessigkeit_score = fields.Integer(
        string="Zuverlässigkeit",
        compute="_compute_zahlungskennzahlen",
        store=True,
        help="0-100. Höher = zahlt zuverlässiger/pünktlicher.",
    )
    zahlungs_bewertung = fields.Selection(
        selection=[
            ("gut", "Gut"),
            ("mittel", "Mittel"),
            ("schlecht", "Schlecht"),
        ],
        string="Bewertung",
        compute="_compute_zahlungskennzahlen",
        store=True,
    )
    skonto_verpasst_summe = fields.Monetary(
        string="Verpasstes Skonto (Summe)",
        compute="_compute_zahlungskennzahlen",
        store=True,
        currency_field="currency_id",
        help="Summe aller verpassten Skontobeträge.",
    )

    @api.depends(
        "invoice_ids.zahlungsverzug_tage",
        "invoice_ids.ist_bezahlt",
        "invoice_ids.payment_state",
        "invoice_ids.state",
        "invoice_ids.skonto_status",
        "invoice_ids.skonto_moeglich",
    )
    def _compute_zahlungskennzahlen(self):
        heute = fields.Date.today()
        for partner in self:
            rechnungen = partner.invoice_ids.filtered(
                lambda m: m.move_type in ("out_invoice", "in_invoice")
                and m.state == "posted"
            )
            bezahlte = rechnungen.filtered("ist_bezahlt")

            # Durchschnittlicher Verzug
            if bezahlte:
                summe = sum(bezahlte.mapped("zahlungsverzug_tage"))
                partner.durchschnitt_verzug = summe / len(bezahlte)
            else:
                partner.durchschnitt_verzug = 0.0

            # Überfällige (offen + Fälligkeit überschritten)
            ueberfaellig = rechnungen.filtered(
                lambda m: m.payment_state == "not_paid"
                and m.invoice_date_due
                and m.invoice_date_due < heute
            )
            partner.anzahl_ueberfaellig = len(ueberfaellig)

            # Verpasstes Skonto (Summe)
            verpasst = rechnungen.filtered(
                lambda m: m.skonto_status == "verpasst"
            )
            partner.skonto_verpasst_summe = sum(verpasst.mapped("skonto_moeglich"))

            # Score + Bewertung
            partner.zuverlaessigkeit_score = partner._berechne_score(
                partner.durchschnitt_verzug, partner.anzahl_ueberfaellig
            )
            partner.zahlungs_bewertung = partner._score_zu_bewertung(
                partner.zuverlaessigkeit_score
            )

    def _berechne_score(self, avg_verzug, anzahl_ueberfaellig):
        self.ensure_one()
        score = 100
        # Pro Tag durchschnittlichem Verzug 3 Punkte Abzug
        if avg_verzug > 0:
            score -= int(avg_verzug * 3)
        # Pro überfälliger Rechnung 5 Punkte Abzug
        score -= anzahl_ueberfaellig * 5
        # Auf 0-100 begrenzen
        return max(0, min(100, score))

    def _score_zu_bewertung(self, score):
        self.ensure_one()
        if score >= 80:
            return "gut"
        elif score >= 50:
            return "mittel"
        return "schlecht"
    
    @api.model
    def cron_zahlungsverhalten_pruefen(self):
        params = self.env["ir.config_parameter"].sudo()
        score_schwelle = int(
            params.get_param("zahlungscockpit.score_schwelle", 50)
        )
        skonto_schwelle = float(
            params.get_param("zahlungscockpit.skonto_schwelle", 100.0)
        )

        auffaellige = self.search([
            "|",
            ("zuverlaessigkeit_score", "<", score_schwelle),
            ("skonto_verpasst_summe", ">", skonto_schwelle),
        ])

        buchhaltung = self.env.ref(
            "account.group_account_invoice", raise_if_not_found=False
        )
        if not buchhaltung or not buchhaltung.users:
            return

        for partner in auffaellige:
            bestehend = self.env["mail.activity"].search_count([
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner.id),
                ("activity_type_id", "=",
                 self.env.ref("mail.mail_activity_data_todo").id),
            ])
            if bestehend:
                continue
            grund = partner._warnungs_grund(score_schwelle, skonto_schwelle)
            partner.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("Zahlungsverhalten prüfen: %s") % partner.name,
                note=grund,
                user_id=buchhaltung.users[0].id,
            )

    def _warnungs_grund(self, score_schwelle, skonto_schwelle):
        self.ensure_one()
        gruende = []
        if self.zuverlaessigkeit_score < score_schwelle:
            gruende.append(
                _("Niedriger Score: %s") % self.zuverlaessigkeit_score
            )
        if self.skonto_verpasst_summe > skonto_schwelle:
            gruende.append(
                _("Verpasstes Skonto: %.2f") % self.skonto_verpasst_summe
            )
        return " | ".join(gruende)