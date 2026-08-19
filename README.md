# Odoo QM- & Prozess-Suite

Drei aufeinander aufbauende Odoo-Module für einen produzierenden Betrieb (Kosmetik / Nahrungsergänzung), die Qualitätsmanagement, Buchhaltung und Fertigung zu einem durchgängigen Prozess verbinden. Jedes Modul löst ein reales Problem, das der Odoo-Standardkatalog nicht abdeckt.

> Getestet mit **Odoo 17** (Community). Entwicklung über Docker.

---

## Überblick

| Modul | Domäne | Nutzen in einem Satz |
|-------|--------|----------------------|
| `qm_freigabe` | Lager / QM | Chargen dürfen erst ausgeliefert werden, wenn QM sie freigegeben hat — konfigurierbar als Warnung oder harte Sperre. |
| `zahlungscockpit` | Buchhaltung | Bewertet das Zahlungsverhalten pro Kunde/Lieferant und macht verschenktes Skonto sichtbar. |
| `mrp_qm_tracking` | Fertigung | Vollständige Chargen-Rückverfolgung Rohstoff ↔ Produkt, gekoppelt an die QM-Freigabe, mit Rückruf-Werkzeug. |

Die Module funktionieren einzeln, entfalten aber zusammen ihren eigentlichen Wert: Sie bilden einen **durchgängigen Prozess über drei Abteilungen** ab.

```
Rohstoff-QM  ──►  Produktion  ──►  Produkt-QM  ──►  Auslieferung
(qm_freigabe)   (mrp_qm_tracking)  (qm_freigabe)    (qm_freigabe)
```

---

## Module im Detail

### 1. `qm_freigabe` — Chargen-Qualitätsfreigabe

Ein Freigabe-Workflow für Chargen mit Sperrlogik an der Auslieferung.

- Eigenes Workflow-Modell (`qm.freigabe`) mit Statusleiste: Entwurf → In Prüfung → Freigegeben / Gesperrt
- Automatische Referenznummern über eine Sequenz (`QM/0001`)
- Erweitert `stock.lot` um einen QM-Status (related field)
- **Konfigurierbare Sperre**: Auslieferung nicht freigegebener Chargen wird je nach Einstellung nur gewarnt oder hart blockiert
- Rollen- und Rechtesystem (QM-Mitarbeiter / QM-Manager) mit automatischer Aufgabenzuweisung
- Protokollierte Statuswechsel über den Chatter (Audit-Spur)

### 2. `zahlungscockpit` — Zahlungsverhalten-Cockpit

Bewertet, wie zuverlässig Partner zahlen — für Kunden und Lieferanten.

- Berechnet pro Rechnung den Zahlungsverzug (Tage über/unter Fälligkeit)
- Aggregiert pro Partner: Ø-Verzug, überfällige Rechnungen, Zuverlässigkeits-Score (0–100), Bewertung
- **Skonto-Analyse**: erkennt genutztes und verpasstes Skonto und summiert verschenktes Geld pro Lieferant (versionsrobust umgesetzt)
- Konfigurierbare Warnschwellen
- Wöchentlicher Cron benachrichtigt die Buchhaltung bei auffälligen Partnern
- Dashboard mit Graph- und Pivot-Ansicht

### 3. `mrp_qm_tracking` — Fertigung mit Chargen-Rückverfolgung

Verbindet Produktion mit dem QM-Modul und macht Chargen rückverfolgbar.

- Blockiert Fertigungsaufträge, die gesperrte Rohstoff-Chargen einsetzen
- Erzeugt beim Produktionsabschluss automatisch eine QM-Freigabe für die produzierte Charge (die dann das Auslieferungs-Gate scharf schaltet)
- Speichert die vollständige Verknüpfung Rohstoff-Charge ↔ Produkt-Charge dauerhaft
- **Rückruf-Werkzeug**: von jeder Charge aus per Smart Button in beide Richtungen die betroffenen Chargen finden ("welche Endprodukte enthalten diesen Rohstoff?" und umgekehrt)

Baut auf `qm_freigabe` auf (`depends`).

---

## Installation

Vorausgesetzt wird eine laufende Odoo-17-Instanz. Beispiel mit Docker:

```yaml
# docker-compose.yml (Auszug)
services:
  web:
    image: odoo:17
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

1. Die Modulordner nach `./addons/` legen.
2. `docker compose up -d`
3. In Odoo den Entwicklermodus aktivieren, Apps-Liste aktualisieren.
4. Module installieren. Reihenfolge/Abhängigkeiten:
   - `qm_freigabe` benötigt `stock`, `mail`
   - `zahlungscockpit` benötigt `account`, `mail`
   - `mrp_qm_tracking` benötigt `mrp`, `qm_freigabe` (installiert `qm_freigabe` bei Bedarf mit)

---

## Tests

Jedes Modul bringt automatisierte Tests mit (`TransactionCase`). Ausführen z. B.:

```bash
docker compose exec web odoo -u qm_freigabe -d <DB_NAME> --test-enable --stop-after-init
docker compose exec web odoo -u zahlungscockpit -d <DB_NAME> --test-enable --stop-after-init
docker compose exec web odoo -u mrp_qm_tracking -d <DB_NAME> --test-enable --stop-after-init
```

---

