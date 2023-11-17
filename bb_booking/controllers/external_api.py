#copyright © Simone Tullino 08/11
import requests

from odoo import http, fields
from odoo.http import request, Response, _logger
from odoo.tools.safe_eval import json, datetime
import json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
#*****************************************prova*****************
#https://odoo16-prenotazione-bb.unitivastaging.it/api/prova

#*********************route****************************

def fetch_room_cleaning_details(pms_product_id):
    url = "https://api.octorate.com/connect/rest/v1/pms"
    # Usa il token statico qui
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer 5fc9e202a3ce46c592bb793b3a70a6adHRGYUDTYFO'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        for room in data:
            if room["id"] == pms_product_id:
                return room.get("clean"), room.get("lastCleaningDate"), room.get("name")
    return None, None, None


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
            data_creazione_ = content.get("createTime")
            note_interne_= content.get("channelNotes")
            # **info cliente**
            guests = content.get("guests")
            checkin_ = guests[0].get("checkin")
            checkout_ = guests[0].get("checkout")
            city_ = guests[0].get("city")
            email_ = guests[0].get("email")
            phone_ = guests[0].get("phone")
            address_ = guests[0].get("address")
            effettivo_Checkin = content.get("effectiveCheckin")
            effettivo_Checkout = content.get("effectiveCheckout")
            tipo_pagamento = content.get("paymentType")
            stato_pagamento = content.get("paymentStatus")

            tipo = data_dict.get('type')

            #gestione della tipologia della camera
            # psm = content.get("pmsProduct")
            # id_to_room_name = {
            #     "599451": "Sky 001 Real Room",
            #     "599455": "Los Angeles Apartment 101",
            #     "612859": "quadrupla sepa"
            #     # Aggiungi altre associazioni ID-nome qui secondo necessità
            # }
            # room_name = id_to_room_name.get(str(psm))
            #piattaforma di prenotazione
            piattaforma = content.get("channelName")

            checkin_date = fields.Date.from_string(checkin_)
            checkout_date = fields.Date.from_string(checkout_)
            data_creazione_mod = fields.Date.from_string(data_creazione_)
            delta = checkout_date - checkin_date
            n_notti = delta.days
            quantity_soggiorno = totalGuest_ * n_notti
            nome_stanza = content.get("roomName")

            # gestione della tipologia della camera
            pms_product_id = content.get("pmsProduct")
            clean, last_cleaning_date, name = fetch_room_cleaning_details(pms_product_id)



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
                "nome stanza" : nome_stanza,
                "creazione fattura" : data_creazione_,
                "nota Interna": note_interne_,
                #"Tipologia prodotto id": psm,
                #"Tipologia camera": room_name,
                "Piattaforma di prenotazione": piattaforma,
                "Checkin effettuato": effettivo_Checkin,
                "Checkout effettuato": effettivo_Checkout,
                "Tipo pagamento": tipo_pagamento,
                "Stato pagamento": stato_pagamento,
                "Stato camera": 'Clean' if clean else 'Not Clean',
                "Ultima pulizia": last_cleaning_date,
                "Tipologia camera": name
            }
            #creazione piattaforma

            team_vendite = request.env['crm.team'].sudo().search([('name','=',piattaforma)], limit=1)
            if not team_vendite:
                team_vendite = request.env['crm.team'].sudo().create({'name': piattaforma})

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
                    'partner_id': intero_contact,  # Utilizza l'ID del contatto come partner_id
                    'invoice_date': data_creazione_mod,
                    #'ref': room_name,
                    'team_id': team_vendite.id,
                    'email_utente': email_,
                    'telefono_utente': phone_,
                    'nome_stanza_utente': nome_stanza,
                    'nota_interna': note_interne_,
                    'checkin_effettuato': effettivo_Checkin,
                    'checkout_effettuato': effettivo_Checkout,
                    'stato_del_pagamento': stato_pagamento,
                    'tipo_di_pagamento': tipo_pagamento,
                    'pulizia_camera': clean,
                    'ultima_pulizia': last_cleaning_date,
                    'tipologia_camera': name,

                })

                # Creazione delle linee della fattura
                linee_fattura = []

                # Linea per il prodotto 1 (Pernotto)
                linea_fattura_pernotto = {
                    'move_id': room_booking_obj.id,
                    'product_id': room_product.id,  # ID del prodotto 'Pernotto' nel portale amministrazione
                    'name': f"Prenotazione {refer_} dal {checkin_} al {checkout_}",
                    'quantity': 1,
                    'price_unit': roomGross_,
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
                         f"<span style='color:red; font-weight:bold;'>Note interne: {note_interne_}</span><br>"
                         f"Nome stanza: {nome_stanza}<br>"
                         f"Nome camera: {name}<br>"
                         f"Pulizia camera:{clean}<br>"
                         f"Ultima pulizia:{last_cleaning_date}<br>"
                         f"Piattaforma di prenotazione: {piattaforma}<br>"
                         f"Check in effettuato: {effettivo_Checkin} <br>"
                         f"Check out effettuato: {effettivo_Checkout} <br>"
                         f"Stato del pagamento: {stato_pagamento} <br>"
                         f"Tipo di pagamento: {tipo_pagamento} </pr>",
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
                        'invoice_date': data_creazione_mod,  # DOMANDA:  DEVO AGGIUNGERE LA DATA DI MODIFICA?
                        # 'partner_id': intero_contact  # Utilizza l'ID del contatto come partner_id
                        #'ref': room_name,
                        'team_id': team_vendite.id,
                        'email_utente': email_,
                        'telefono_utente': phone_,
                        'nome_stanza_utente': nome_stanza,
                        'tipologia_camera': name,
                        'pulizia_camera': clean,
                        'ultima_pulizia': last_cleaning_date,
                        'nota_interna': note_interne_,
                        'checkin_effettuato': effettivo_Checkin,
                        'checkout_effettuato': effettivo_Checkout,
                        'stato_del_pagamento': stato_pagamento,
                        'tipo_di_pagamento': tipo_pagamento
                    })

                    existing_invoice_line_ids = existing_invoice.invoice_line_ids

                    # Modifica le linee di fattura esistenti
                    for line in existing_invoice_line_ids:
                        if line.product_id.id == room_product.id:  # ID del prodotto 'Pernotto'
                            # Aggiorna le informazioni relative al prodotto 'Pernotto'
                            line.write({
                                'name': f"Prenotazione {refer_} dal {checkin_} al {checkout_}",
                                'quantity': 1,
                                'price_unit': roomGross_
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







