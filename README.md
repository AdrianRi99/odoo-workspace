# QM Chargenfreigabe für Odoo 17

Ein Odoo-Modul, das einen **Qualitätssicherungs-Freigabeprozess für Chargen**
einführt und die Auslieferung nicht freigegebener Ware verhindert. Gebaut für
Produktionsbetriebe (z. B. Kosmetik, Nahrungsergänzung), in denen Chargen erst
nach QM-Freigabe das Lager verlassen dürfen.

Odoo kennt zwar Chargen (`stock.lot`), aber keinen dedizierten
Freigabe-Workflow mit Auslieferungssperre – genau diese Lücke schließt das Modul.

## Funktionen

- **Freigabe-Workflow** mit Statusbar (Entwurf → In Prüfung → Freigegeben, plus Sonderzustand Gesperrt).
- **Automatische Referenznummern** (`QM/0001`, …) über eine Sequenz.
- **Chargen-Anbindung**: Verknüpfung mit `stock.lot`, Freigabestatus per *related field* an die Charge gespiegelt.
- **Konfigurierbare Auslieferungssperre**: nicht freigegebene Charge wird je nach Einstellung **hart blockiert** oder **nur gewarnt**.
- **Rollen & Rechte**: hierarchische Gruppen *QM-Mitarbeiter* / *QM-Manager*.
- **Automatische Aufgabenzuweisung**: QM-Manager erhalten bei Prüfungsbeginn eine Odoo-Aktivität.
- **Audit-Spur** über den Chatter (`tracking`) und **automatisierte Tests** (`TransactionCase`).

## Technische Bausteine

`_inherit` (stock.lot, stock.picking, res.config.settings) · Mixins (mail.thread, mail.activity.mixin) · related field · überschriebenes `create` und `button_validate` · `ir.config_parameter` · `res.groups` mit `implied_ids` · ACL via CSV · Statusbar/Buttons/Filter-Views · Unit-Tests mit `assertRaises`.

## Installation

Voraussetzung: Odoo 17 mit **Inventory** (`stock`) und **Discuss** (`mail`); Chargen aktiviert (*Inventory → Konfiguration → Chargen & Seriennummern*).

```bash
docker compose up -d
docker compose exec web odoo -i qm_freigabe -d <DB_NAME> --stop-after-init
docker compose restart web
```

Danach unter *Einstellungen → Benutzer* die Rolle *QM-Manager* zuweisen.

## Tests

```bash
docker compose exec web odoo -u qm_freigabe -d <DB_NAME> --test-enable --stop-after-init
```

## Konfiguration

*Einstellungen → QM Freigabe → Sperrmodus*: **Nur warnen** oder **Hart blockieren**.

## Lizenz

LGPL-3
