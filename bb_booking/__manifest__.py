{
    'name': 'Prenotazione stanze e appartamenti',
    'version': '1.0',
    'author': 'Simone',
    'category': 'Custom Modules',
    'summary': 'Gestisce le fatture dal sito Octorate verso Odoo',
    'description': 'Prenotazione stanze: integrazione con Octorate',
    'depends': ['base', 'account', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/booking_info.xml',
    ],
    'application': False,
    'installable': True,
}
