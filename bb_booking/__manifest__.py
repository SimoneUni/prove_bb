{
    'name': 'Prenotazione stanze e appartamenti',
    'version': '1.0',
    'author': 'Simone',
    'description': 'Prenotazione stanze: integrazione con Octorate',
    'depends': ['base', 'account', 'web','auth_jwt'],
    'data': [
        'security/ir.model.access.csv',
        'data/auth_jwt_validator.xml',
        'views/booking_info.xml',



    ],
    'application': False,
    'installable': True,
}
