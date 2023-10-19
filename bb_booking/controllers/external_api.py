from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import json


class RoomBookingController(http.Controller):
    @http.route('/api/your_endpoint', auth='public', methods=['POST'], csrf=False)
    def handle_custom_endpoint(self, **post):
        json_data = request.httprequest.data
        try:
            data_dict = json.loads(json_data)
        except ValueError:
            return "Errore nella formattazione dei dati JSON"

            # Estrai il valore del campo 'checkin' dal dizionario dei dati
        checkin_date = data_dict.get('checkin')
        contact_data = data_dict.get('guests')[0]  # Poiché sembra che ci sia solo un ospite
        name = f"{contact_data.get('givenName')} {contact_data.get('familyName')}"
        zip_code = contact_data.get('zipcode')
        country_id = contact_data.get('country_id')  # Assicurati che questo sia un valore valido per res.country
        state_id = contact_data.get('state_id')  # Assicurati che questo sia un valore valido per res.country.state
        street_name = contact_data.get('street_name')
        street_number = contact_data.get('street_number')
        street_number2 = contact_data.get('street_number2')
        city_id = contact_data.get('city_id')  # Assicurati che questo sia un valore valido per res.city

        # Assicurati che il campo 'partner_id' sia stato fornito nel JSON
        partner_obj = request.env['res.partner']
        new_partner = partner_obj.create({
            'name': name,
            'zip': zip_code,
            'country_id': country_id,
            'state_id': state_id,
            'street_name': street_name,
            'street_number': street_number,
            'street_number2': street_number2,
            'city_id': city_id,
        })

        # Ora, crea una nuova istanza del tuo modello con i campi 'checkin' e 'partner_id' impostati
        room_booking_obj = request.env['account.move']
        new_room_booking = room_booking_obj.create({
            'checkin': checkin_date,
            'partner_id': new_partner.id,
            # Altri campi del tuo modello che devono essere impostati
        })

        return (new_room_booking)

# from odoo import http
# from odoo.http import request
# import json
#
# class ThirdPartyConnector(http.Controller):
#     @http.route('/third_party_connector/receive_data', type='json', auth='user', methods=['POST'], csrf=False)
#     def receive_data(self, **kwargs):
#         data = request.jsonrequest
#
#         if data:
#             try:
#                 model = "account.move"
#                 type = data.get('type')
#
#                 # Estrazione dati dal JSON
#                 content_data = json.loads(data.get('content')) if data.get('content') else {}
#
#                 # Fiedls di interesse
#                 fields = {
#                     'refer': content_data.get('refer'),
#                     'checkin': content_data.get('checkin').split('T')[0] if content_data.get('checkin') else False,
#                     'checkout': content_data.get('checkout').split('T')[0] if content_data.get('checkout') else False,
#                     'totalGuest': content_data.get('totalGuest'),
#                     'totalChildren': content_data.get('children'),
#                     'totalInfants': content_data.get('infants'),
#                     'rooms': content_data.get('rooms'),
#                     'roomGross': content_data.get('roomGross'),
#                     # altri fields possono essere aggiunti qui in base alle necessità
#                 }
#
#                 if type == 'RESERVATION_CREATED':
#
#                     fields['state'] = 'draft'
#                     record = request.env[model].create(fields)
#                     return {'success': True, 'record_id': record.id}
#
#                 elif type in ['RESERVATION_CANCELLED', 'RESERVATION_CONFIRMED']:
#                     # cerca il record esistente tramite ID di riferimento, aggiorna lo stato e lascia invariati gli altri campi
#                     refer_id = fields.get('refer')
#                     record = request.env[model].search([('refer', '=', refer_id)])
#
#
#
#                 else:
#                     return {'error': 'Invalid type'}
#
#             except Exception as e:
#                 return {'error': str(e)}
#
#         return {'error': 'Invalid data'}