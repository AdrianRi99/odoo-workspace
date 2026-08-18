from odoo import models, fields, api
from datetime import timedelta


class AccountMove(models.Model):
    _inherit = "account.move"

    zahlungsverzug_tage = fields.Integer(
        string="Zahlungsverzug (Tage)",
        compute="_compute_zahlungsverzug",
        store=True,
        help="Positiv = zu spät bezahlt, negativ = früher als fällig.",
    )
    ist_bezahlt = fields.Boolean(
        string="Vollständig bezahlt",
        compute="_compute_zahlungsverzug",
        store=True,
    )

    @api.depends("payment_state", "invoice_date_due")
    def _compute_zahlungsverzug(self):
        for move in self:
            move.zahlungsverzug_tage = 0
            move.ist_bezahlt = False
            if move.move_type not in ("out_invoice", "in_invoice"):
                continue
            if move.payment_state in ("paid", "in_payment") and move.invoice_date_due:
                zahldatum = move._letztes_zahldatum()
                if zahldatum:
                    move.ist_bezahlt = True
                    delta = (zahldatum - move.invoice_date_due).days
                    move.zahlungsverzug_tage = delta

    def _letztes_zahldatum(self):
        self.ensure_one()
        zahlungen = self._get_reconciled_payments()
        if not zahlungen:
            return False
        return max(zahlungen.mapped("date"))
    
    skonto_moeglich = fields.Monetary(
        string="Mögliches Skonto",
        compute="_compute_skonto",
        store=True,
        currency_field="currency_id",
        help="Skontobetrag, der bei fristgerechter Zahlung möglich (gewesen) wäre.",
    )
    skonto_status = fields.Selection(
        selection=[
            ("kein", "Kein Skonto"),
            ("offen", "Skonto noch möglich"),
            ("genutzt", "Skonto genutzt"),
            ("verpasst", "Skonto verpasst"),
        ],
        string="Skonto-Status",
        compute="_compute_skonto",
        store=True,
    )

    @api.depends(
        "invoice_payment_term_id",
        "payment_state",
        "invoice_date",
        "amount_total",
        "zahlungsverzug_tage",
        "ist_bezahlt",
    )
    def _compute_skonto(self):
        heute = fields.Date.today()
        for move in self:
            move.skonto_moeglich = 0.0
            move.skonto_status = "kein"
            if move.move_type not in ("out_invoice", "in_invoice"):
                continue
            term = move.invoice_payment_term_id
            skonto_prozent, skonto_tage = move._skonto_konditionen(term)
            if not skonto_prozent or not move.invoice_date:
                continue

            move.skonto_moeglich = move.amount_total * (skonto_prozent / 100.0)
            skonto_frist = move.invoice_date + timedelta(days=skonto_tage)

            if move.ist_bezahlt:
                zahldatum = move._letztes_zahldatum()
                if zahldatum and zahldatum <= skonto_frist:
                    move.skonto_status = "genutzt"
                else:
                    move.skonto_status = "verpasst"
            else:
                if heute <= skonto_frist:
                    move.skonto_status = "offen"
                else:
                    move.skonto_status = "verpasst"

    def _skonto_konditionen(self, term):
        """Liest Skontosatz (%) und -frist (Tage) aus den Zahlungsbedingungen."""
        self.ensure_one()
        if not term:
            return 0.0, 0
        prozent = getattr(term, "discount_percentage", 0.0) or 0.0
        tage = getattr(term, "discount_days", 0) or 0
        return prozent, tage