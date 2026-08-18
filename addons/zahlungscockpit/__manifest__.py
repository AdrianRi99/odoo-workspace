{
    "name": "Zahlungsverhalten-Cockpit",
    "version": "1.0",
    "depends": ["account", "mail"],
    "data": [
        "data/cron.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}