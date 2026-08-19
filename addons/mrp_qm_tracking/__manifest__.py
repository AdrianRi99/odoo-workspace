{
    "name": "MRP QM-Rückverfolgung",
    "version": "1.0",
    "depends": ["mrp", "qm_freigabe"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",
        "views/qm_rueckverfolgung_views.xml",
        "views/stock_lot_views.xml",
    ],
    "installable": True,
    "application": True,
}