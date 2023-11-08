#copyright © Simone Tullino 08/11
from odoo import http, fields
from odoo.http import request, Response, _logger
from odoo.tools.safe_eval import json
#*****************************************prova*****************

#link https://odoo16-prenotazione-bb.unitivastaging.it/api/test

#*********************route****************************

# class AccountController(http.Controller):
#     @http.route('/api/get_accounts', auth='public', csrf=False)
#     def get_accounts(self):
#         account_model = http.request.env['account.account']
#         accounts = account_model.sudo().search([])
#
#         account_list = []
#         for account in accounts:
#             account_info = {
#                 'id': account.id,
#                 'name': account.name,
#                 'code': account.code,
#             }
#             account_list.append(account_info)
#
#         return account_list
# class MyController(http.Controller):
#
#     @http.route('/print_invoices', type='http', auth='public', csrf=False)
#     def print_invoices(self):
#         invoice_records = request.env['account.move'].sudo().search([])
#         for invoice in invoice_records:
#             print("ID FATTURA : ", invoice.id)
#             print("Referenza:", invoice.refer)
#             print("Stato:", invoice.state)
#         return "postate"
# class Fatture(http.Controller):
#     @http.route('/api/getfatture' , auth='public', csrf="*")
#     def get_fatture(self):
#         tutte_lefatture = http.request.env['accoun.move']
#         fatture = tutte_lefatture.sudo().search([])

#https://odoo16-prenotazione-bb.unitivastaging.it/api/prova
class RoomBookingController(http.Controller):
    @http.route('/api/prova', cors='*', auth='public', methods=['POST'], csrf=False, website=False)

   #gestione degli id dinamici

    #MAIN
    def handle_custom_endpoint(self, **post):
        try:
            json_data = request.httprequest.data
            data_dict = json.loads(json_data)
            _logger.info(f"Received data: {data_dict}")

            if 'ping' in data_dict:
                _logger.info("Ping received")
                return Response("Pong", content_type='text/plain', status=200)

            content = json.loads(data_dict.get("content"))

            # Estrai il valore del campo 'checkin' dal dizionario dei dati
            refer_ = content.get("refer")
            guestsList_ = content.get("guestsList")
            roomGross_ = content.get("roomGross")
            totalGuest_ = content.get("totalGuest")
            numero_stanza_ = content.get("rooms")
            priceBreakdown = content.get("priceBreakdown")
            prezzo_unitario_ = priceBreakdown[0].get("price")
            # **info cliente**
            guests = content.get("guests")
            checkin_ = guests[0].get("checkin")
            checkout_ = guests[0].get("checkout")
            city_ = guests[0].get("city")
            email_ = guests[0].get("email")
            phone_ = guests[0].get("phone")
            address_ = guests[0].get("address")

            tipo = data_dict.get('type')

            checkin_date = fields.Date.from_string(checkin_)
            checkout_date = fields.Date.from_string(checkout_)
            delta = checkout_date - checkin_date
            n_notti = delta.days
            quantity_soggiorno = totalGuest_ * n_notti
            nome_stanza = content.get("roomNameGuest")

            response_data = {
                "refer": refer_,
                "prezzo totale": roomGross_,
                "ospiti": totalGuest_,
                "checkin": checkin_,
                "checkout": checkout_,
                "numero stanza": numero_stanza_,
                "numero notti": n_notti,
                "quantity_soggiorno": quantity_soggiorno,
                "prezzo unitario": prezzo_unitario_,
                "city_utente": city_,
                "email": email_,
                "guestsList": guestsList_,
                "telefono": phone_,
                "indirizzo": address_,
                "tipo": tipo,
                "nome stanza" : nome_stanza

            }

            # Creazione della fattura
            room_booking_obj = []  # Inizializza la variabile come False
            customer_invoice_journal = request.env['account.journal'].sudo().search([('type', '=', 'sale')], limit=1)
            customer_account = request.env['account.account'].sudo().search([('name', '=', 'Merci c/vendite')], limit=1)
            room_product = request.env['product.product'].sudo().search([('name', '=', nome_stanza)], limit=1)
            if not room_product:
                room_product = request.env['product.product'].sudo().create({'name': nome_stanza})
            tassa_soggiorno = request.env['product.product'].sudo().search([('name', '=', "Tassa soggiorno")], limit=1)

            if tipo == 'RESERVATION_CREATED':
                # ********CONTROLLO/CREAZIONE DEL CONTATTO******
                contact_bb = request.env['res.partner'].sudo().create({
                    'company_type': 'person',
                    'name': guestsList_,
                    'street': address_,
                    'city': city_,
                    'email': email_,
                    'phone': phone_
                })

                # stampa l'ID del contatto appena creato
                contact_id = contact_bb.id
                intero_contact = int(contact_id)
                print("ID CONTATTO CREATO : ", intero_contact)



                room_booking_obj = request.env['account.move'].sudo().create({
                    'state': 'draft',
                    'journal_id': customer_invoice_journal.id,
                    'refer': refer_,
                    'move_type': 'out_invoice',
                    'checkin': checkin_,
                    'checkout': checkout_,
                    'totalGuest': totalGuest_,
                    'rooms': n_notti,
                    'roomGross': roomGross_,
                    'partner_id': intero_contact  # Utilizza l'ID del contatto come partner_id
                })

                # Creazione delle linee della fattura
                linee_fattura = []

                # Linea per il prodotto 1 (Pernotto)
                linea_fattura_pernotto = {
                    'move_id': room_booking_obj.id,
                    'product_id': room_product.id,  # ID del prodotto 'Pernotto' nel portale amministrazione
                    'name': f"Prenotazione {refer_} dal {checkin_} al {checkout_}",
                    'quantity': n_notti,
                    'price_unit': prezzo_unitario_,
                    'account_id': customer_account.id
                }
                linee_fattura.append(linea_fattura_pernotto)

                # Linea per il prodotto 2 (Tassa di Soggiorno)
                linea_fattura_tassasoggiorno = {
                    'move_id': room_booking_obj.id,
                    'product_id': tassa_soggiorno.id,  # ID del prodotto 'Tassa di Soggiorno' nel portale amministrazione
                    'name': "Tassa di soggiorno",
                    'quantity': quantity_soggiorno,
                    'account_id': customer_account.id
                }
                linee_fattura.append(linea_fattura_tassasoggiorno)
                for line in linee_fattura:
                    request.env['account.move.line'].sudo().create(line)

                room_booking_obj.with_context(default_type='out_invoice').write({'state': 'draft'})
                room_booking_obj.message_post(
                    body=f"<p><b><font size='4' face='Arial'>Riepilogo dei dati:</font></b><br>"
                         f"Refer: {refer_}<br>"
                         f"Prezzo totale: {roomGross_}<br>"
                         f"Ospiti: {totalGuest_}<br>"
                         f"Checkin: {checkin_}<br>"
                         f"Checkout: {checkout_}<br>"
                         f"Numero stanza: {numero_stanza_}<br>"
                         f"Numero notti: {n_notti}<br>"
                         f"Quantity soggiorno: {quantity_soggiorno}<br>"
                         f"Prezzo unitario: {prezzo_unitario_}<br>"
                         f"City utente: {city_}<br>"
                         f"Email: {email_}<br>"
                         f"Guests List: {guestsList_}<br>"
                         f"Telefono: {phone_}<br>"
                         f"Indirizzo: {address_}<br>"
                         f"Nome stanza: {nome_stanza}<br></p>",
                    message_type='comment'
                )


            # *************************************************************************************
            elif tipo == 'RESERVATION_CHANGE':

                existing_invoice = request.env['account.move'].sudo().search([

                    ('refer', '=', refer_),

                    ('move_type', '=', 'out_invoice')

                ], limit=1)



                if existing_invoice:
                    existing_invoice.write({
                        'state': 'draft',
                        'journal_id': customer_invoice_journal.id,
                        'refer': refer_,
                        'move_type': 'out_invoice',
                        'checkin': checkin_,
                        'checkout': checkout_,
                        'totalGuest': totalGuest_,
                        'roomGross': roomGross_,
                        # 'partner_id': intero_contact  # Utilizza l'ID del contatto come partner_id
                    })

                    existing_invoice_line_ids = existing_invoice.invoice_line_ids

                    # Modifica le linee di fattura esistenti
                    for line in existing_invoice_line_ids:
                        if line.product_id.id == room_product.id:  # ID del prodotto 'Pernotto'
                            # Aggiorna le informazioni relative al prodotto 'Pernotto'
                            line.write({
                                'name': f"Prenotazione {refer_} dal {checkin_} al {checkout_}",
                                'quantity': n_notti,
                                'price_unit': prezzo_unitario_
                                # Aggiungi altri campi da aggiornare
                            })
                        elif line.product_id.id == tassa_soggiorno.id:  # ID del prodotto 'Tassa di Soggiorno'
                            # Aggiorna le informazioni relative al prodotto 'Tassa di Soggiorno'
                            line.write({
                                'name': "Tassa di soggiorno",
                                'quantity': quantity_soggiorno
                                # Aggiungi altri campi da aggiornare
                            })

                room_booking_obj = existing_invoice
                room_booking_obj.message_post(
                    body=f"<p><b><font size='4' face='Arial'>Dati aggiornati:</font></b><br>"
                         f"Refer: {refer_}<br>"
                         f"Prezzo totale: {roomGross_}<br>"
                         f"Ospiti: {totalGuest_}<br>"
                         f"Checkin: {checkin_}<br>"
                         f"Checkout: {checkout_}<br>"
                         f"Numero stanza: {numero_stanza_}<br>"
                         f"Numero notti: {n_notti}<br>"
                         f"Quantity soggiorno: {quantity_soggiorno}<br>"
                         f"Prezzo unitario: {prezzo_unitario_}<br>"
                         f"City utente: {city_}<br>"
                         f"Email: {email_}<br>"
                         f"Guests List: {guestsList_}<br>"
                         f"Telefono: {phone_}<br>"
                         f"Indirizzo: {address_}<br>"
                         f"Nome stanza: {nome_stanza}<br></p>",
                    message_type='comment'
                )

                # ************************************************************************


            elif tipo == 'RESERVATION_CANCELLED':

                # Cerca la fattura esistente basata su 'refer' e 'move_type'

                existing_invoice = request.env['account.move'].sudo().search([

                    ('refer', '=', refer_),

                    ('move_type', '=', 'out_invoice')

                ], limit=1)

                if existing_invoice:
                    # Imposta lo stato della fattura esistente a 'cancel'

                    existing_invoice.write({

                        'state': 'cancel'

                    })

                    # Assegna la fattura esistente all'oggetto room_booking_obj

                    room_booking_obj = existing_invoice


            print("La fattura ha il seguyente id ---------->", room_booking_obj.id)

            # room_booking_obj.action_post()
            print("postata")
            return Response(json.dumps(response_data), content_type='application/json')
        except json.JSONDecodeError as e:
            _logger.error(f"JSON Decode Error: {e}")
            return Response("Invalid JSON format", content_type='text/plain', status=400)
        except Exception as e:
            _logger.exception("An unexpected error occurred")
            return Response("Internal Server Error", content_type='text/plain', status=500)









     # ***** TASSA SOGIORNO ******
# delta = checkout - check in
# n_notti = delta.days
#quantity = numero_ospiti*delta

    # ***** PERNOTTO *******



#name = f"Prenotazione {invoice.refer} dal {checkin} al {checkout}"
#quantity = numero stanze

        # room_booking_obj = request.env['account.move']
        # new_invoice = room_booking_obj.sudo().create({
        #     'refer': refer,
        #     'checkin': checkin,
        #     'checkout': checkout,
        #     'totalGuest': totalGuest,
        #     'roomGross': roomGross,
        #     'partner_id': 36
        #     # Altri campi del tuo modello che devono essere impostati
        # })

#********************************************************************************************************
# else:
#     print("fallito")
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