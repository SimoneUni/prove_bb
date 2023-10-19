{
    'name': 'Prenotazione stanze e appartamenti',
    'version': '1.0',
    'author': 'Simone',
    'description': 'Prenotazione stanze: integrazione con Octorate',
    'depends': ['base', 'account', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/booking_info.xml',
        'views/menu.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'controllers': [
        'bb_booking.controllers.external_api.RoomBookingController',
    ],
}
