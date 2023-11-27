#copyright © Simone Tullino 08/11
import requests

from odoo import http, fields
from odoo.http import request, Response, _logger
from odoo.tools.safe_eval import json, datetime
from datetime import datetime

import json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
#*****************************************prova*****************
#https://odoo16-prenotazione-bb.unitivastaging.it/api/prova

#*********************route****************************
CLIENT_ID = "public_a3a3b3c2278b4deabd9108e74c5e8af2"
CLIENT_SECRET = "secret_47ff49e5533047a994869a012a94eecfTOIUDRGXYK"

#token di accesso
# def get_access_token():
#     endpoint = "https://api.octorate.com/connect/rest/v1/identity/apilogin"
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     payload = {
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET
#     }
#     response = requests.post(endpoint, data=payload, headers=headers)
#     if response.status_code == 200:
#         return response.json().get("access_token")
#     else:
#         print(f"Errore nell'ottenere il token di accesso: {response.status_code} - {response.text}")
#         return None
#refresh token

token_info = {
    "access_token": "c78cebc7d76c4f8baefac17a762c07b7WYSOATINCX",
    "expireDate": "2023-11-28T15:51:31.928Z[UTC]"
}
#istanza produzione
#refresh_token = "202d09a5186a47928c81f0290e335944"
#istanza test
refresh_token = "2acf003360ea4ebca6871b5d7e56efe2"
def is_token_expired(token_info):
    expire_date_str = token_info.get("expireDate")
    if expire_date_str:
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%dT%H:%M:%S.%fZ[UTC]")
        return datetime.utcnow() > expire_date
    return True

def refresh_access_token(refresh_token):
    url = "https://api.octorate.com/connect/rest/v1/identity/refresh"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        new_access_token = response_data.get("access_token")
        new_expire_date = response_data.get("expireDate")  # Aggiungi qui la logica per estrarre la nuova data di scadenza
        return new_access_token, new_expire_date
    else:
        print(f"Errore nella generazione del nuovo access token: {response.status_code} - {response.text}")
        return None, None

def get_access_token(refresh_token):
    global token_info

    if is_token_expired(token_info):
        new_access_token, new_expire_date = refresh_access_token(refresh_token)
        if new_access_token:
            token_info["access_token"] = new_access_token
            token_info["expireDate"] = new_expire_date  # Aggiornamento della data di scadenza
            return new_access_token
        else:
            print("Impossibile ottenere un nuovo access token.")
            return None
    else:
        return token_info["access_token"]

def fetch_room_cleaning_details(pms_product_id, refresh_token):
    access_token = get_access_token(refresh_token)

    url = "https://api.octorate.com/connect/rest/v1/pms"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", [])
        for room in data:
            if room["id"] == pms_product_id:
                return {
                    "name": room.get("name"),
                    "clean": room.get("clean"),
                    "cleaningDays": room.get("cleaningDays"),
                    "lastCleaningDate": room.get("lastCleaningDate")
                }
    # Restituisci un dizionario vuoto se non trovi una corrispondenza per l'ID.
    return {}
    # elif response.status_code == 401:  # Token scaduto o non valido
    #     new_access_token = refresh_access_token()  # Usa il tuo refresh token qui
    #     if new_access_token:
    #         return fetch_room_cleaning_details(pms_product_id, access_token)
    #     else:
    #         return None, None, None





#_________________________________________



# Funzione per creare le fatture




class RoomBookingController(http.Controller):
    @http.route('/api/prova', cors='*', auth='public', methods=['POST'], csrf=False, website=False)

   #gestione degli id dinamici


    #MAIN
    def handle_custom_endpoint(self, refresh_token=None, **post):
        access_token = get_access_token(refresh_token)

        if access_token:
            print(f"Token di accesso ottenuto con successo: {access_token}")
        else:
            print("Errore nell'ottenere il token di accesso.")
            return

        try:
            print(access_token)
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
            totalChildren_ = content.get("totalChildren")
            totalInfants_ = content.get("totalInfants")
            #calcolo adulti
            totaleAdults = totalGuest_ - totalChildren_ - totalInfants_
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
            quantity_soggiorno = totaleAdults * n_notti
            nome_stanza = content.get("roomName")

            # gestione della tipologia della camera
            pms_product_id = content.get("pmsProduct")
            dettagli_camera = fetch_room_cleaning_details(pms_product_id, refresh_token)
            stato_camera = dettagli_camera.get("clean")
            tipologia_camera = dettagli_camera.get("name")
            ultima_pulizia = dettagli_camera.get("lastCleaningDate")



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
                "Ultima pulizia": ultima_pulizia,
                "Tipologia camera": tipologia_camera,
                "Stato camera": stato_camera,
                "numero totale di adulti": totaleAdults
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
                    'invoice_date': checkin_date,
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
                    'pulizia_camera': stato_camera,
                    'ultima_pulizia': ultima_pulizia,
                    'tipologia_camera': tipologia_camera,
                    'totalChildren': totalChildren_,
                    'totalInfants': totalInfants_,
                    'totale_adulti': totaleAdults


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
                         #f"Refer: {refer_}<br>"
                         f"Prezzo totale: {roomGross_}<br>"
                         f"Ospiti totali: {totalGuest_}<br>"
                         f"Adulti: {totaleAdults}<br>"
                         f"Bambini: {totalChildren_}<br>"
                         f"Neonati: {totalInfants_}<br>"
                         #f"Checkin: {checkin_}<br>"
                         #f"Checkout: {checkout_}<br>"
                         #f"Numero stanza: {numero_stanza_}<br>"
                         f"Numero notti: {n_notti}<br>"
                         #f"Quantity soggiorno: {quantity_soggiorno}<br>"
                         #f"Prezzo unitario: {prezzo_unitario_}<br>"
                         #f"City utente: {city_}<br>"
                         f"Note interne: {note_interne_}<br>"
                         f"Stato del pagamento: {stato_pagamento} <br>"
                         f"Tipo di pagamento: {tipo_pagamento} <br>"
                         f"<p><b><font size='2' face='Arial'>Informazione cliente:</font></b><br>"
                         f"Email: {email_}<br>"
                         #f"Guests List: {guestsList_}<br>"
                         f"Telefono: {phone_}</pr>",
                         #f"Indirizzo: {address_}<br>"
                         #f"Nome stanza: {nome_stanza}<br>"
                         #f"Nome camera: {tipologia_camera}<br>"
                         #f"Pulizia camera:{stato_camera}<br>"
                         #f"Ultima pulizia:{ultima_pulizia}<br>"
                         #f"Piattaforma di prenotazione: {piattaforma}<br>"
                         #f"Check in effettuato: {effettivo_Checkin} <br>"
                         #f"Check out effettuato: {effettivo_Checkout} <br>"
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
                        'invoice_date': checkin_date,  # DOMANDA:  DEVO AGGIUNGERE LA DATA DI MODIFICA?
                        # 'partner_id': intero_contact  # Utilizza l'ID del contatto come partner_id
                        #'ref': room_name,
                        'team_id': team_vendite.id,
                        'email_utente': email_,
                        'telefono_utente': phone_,
                        'nome_stanza_utente': nome_stanza,
                        'tipologia_camera': tipologia_camera,
                        'pulizia_camera': stato_camera,
                        'ultima_pulizia': ultima_pulizia,
                        'nota_interna': note_interne_,
                        'checkin_effettuato': effettivo_Checkin,
                        'checkout_effettuato': effettivo_Checkout,
                        'stato_del_pagamento': stato_pagamento,
                        'tipo_di_pagamento': tipo_pagamento,
                        'totalChildren': totalChildren_,
                        'totalInfants': totalInfants_,
                        'totale_adulti': totaleAdults

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

    @http.route('/api/import', cors='*', auth='public', methods=['GET'], csrf=False, website=False)
    def importazione(self, refresh_token=None, **post):

        access_token = get_access_token(refresh_token)

        if access_token:
            print(f"Token di accesso ottenuto con successo: {access_token}")
        else:
            print("Errore nell'ottenere il token di accesso.")

        url = "https://api.octorate.com/connect/rest/v1/reservation/632966?type=CHECKIN&startDate=2023-12-01"

        # Header della richiesta con il token di autenticazione
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        # Esegui la richiesta GET all'API
        response = requests.get(url, headers=headers)

        # Verifica se la richiesta ha avuto successo
        if response.status_code == 200:
            # Parsa la risposta JSON
            data = response.json()

            response_data_list = []

            # Estrai le prenotazioni dalla lista "data" e cicla su di esse
            for reservation in data.get("data", []):
                refer = reservation.get("refer")
                guests = reservation.get("guests", [])
                for guest in guests:
                    # Ora puoi accedere ai campi dell'oggetto guest direttamente
                    email = guest.get("email")
                    familyName = guest.get("familyName")
                    givenName = guest.get("givenName")
                    phone = guest.get("phone")
                    city = guest.get("city")
                    nome_completo = str(givenName) + " " + str(familyName)
                pmsProduct = reservation.get("pmsProduct")
                totalGross = reservation.get("totalGross")
                channelName = reservation.get("channelName")
                paymentStatus = reservation.get("paymentStatus")
                paymentType = reservation.get("paymentType")
                roomGross = reservation.get("roomGross")
                totalGuest = reservation.get("totalGuest")
                totalChildren = reservation.get("totalChildren")
                totalInfants = reservation.get("totalInfants")
                totaleadulti = totalGuest - totalChildren - totalInfants
                checkin = reservation.get("checkin")
                checkout = reservation.get("checkout")
                createTime = reservation.get("createTime")
                channelNotes = reservation.get("channelNotes")
                roomName = reservation.get("roomName")

                checkin_date = fields.Date.from_string(checkin)
                checkout_date = fields.Date.from_string(checkout)
                data_creazione_mod = fields.Date.from_string(createTime)
                delta = checkout_date - checkin_date
                n_notti = delta.days
                quantity_soggiorno = totaleadulti * n_notti


                # gestione della tipologia della camera
                # gestione della tipologia della camera
                pms_product_id = reservation.get("pmsProduct")
                dettagli_camera = fetch_room_cleaning_details(pms_product_id, refresh_token)
                stato_camera = dettagli_camera.get("clean")
                tipologia_camera = dettagli_camera.get("name")
                ultima_pulizia = dettagli_camera.get("lastCleaningDate")




                # Puoi fare ulteriori operazioni con i dati estratti per ogni prenotazione
                # Ad esempio, stampare i dati
                response_data = {
                    "riferimento": refer,
                    "speriamo romm groos": roomGross,
                    "totalGuest": totalGuest,
                    "checkin": checkin,
                    "checkout": checkout,
                    "createTime": createTime,
                    "channelNotes": channelNotes,
                    "email": email,
                    "Nome Utente": nome_completo,
                    "phone": phone,
                    "city": city,
                    "id comera": pmsProduct,
                    "costo totale": totalGross,
                    "Canale di prenotazione" : channelName,
                    "Stato del pagamento": paymentStatus,
                    "Tipo di pagamento": paymentType,
                    "Nome stanza":  roomName,
                    "Ultima pulizia": ultima_pulizia,
                    "Tipologia camera": tipologia_camera,
                    "Stato camera": stato_camera,
                    "totale adulti": totaleadulti,
                    "totale bambini": totalChildren,
                    "totale neonati": totalInfants
                }

                response_data_list.append(response_data)


                team_vendite = request.env['crm.team'].sudo().search([('name', '=', channelName)], limit=1)
                if not team_vendite:
                    team_vendite = request.env['crm.team'].sudo().create({'name': channelName})

                # Creazione della fattura
                room_booking_obj = []  # Inizializza la variabile come False
                customer_invoice_journal = request.env['account.journal'].sudo().search([('type', '=', 'sale')], limit=1)
                customer_account = request.env['account.account'].sudo().search([('name', '=', 'Merci c/vendite')], limit=1)
                room_product = request.env['product.product'].sudo().search([('name', '=', roomName)], limit=1)
                if not room_product:
                    room_product = request.env['product.product'].sudo().create({'name': roomName})
                tassa_soggiorno = request.env['product.product'].sudo().search([('name', '=', "Tassa soggiorno")], limit=1)


            # ********CONTROLLO/CREAZIONE DEL CONTATTO******
                contact_bb = request.env['res.partner'].sudo().create({
                    'company_type': 'person',
                    'name': nome_completo,
                    'city': city,
                    'email': email,
                    'phone': phone
                })

                # stampa l'ID del contatto appena creato
                contact_id = contact_bb.id
                intero_contact = int(contact_id)
                print("ID CONTATTO CREATO : ", intero_contact)

                room_booking_obj = request.env['account.move'].sudo().create({
                    'state': 'draft',
                    'journal_id': customer_invoice_journal.id,
                    'refer': refer,
                    'move_type': 'out_invoice',
                    'checkin': checkin_date,
                    'checkout': checkout_date,
                    'totalGuest': totalGuest,
                    'rooms': n_notti,
                    'roomGross': roomGross,
                    'partner_id': intero_contact,  # Utilizza l'ID del contatto come partner_id
                    'invoice_date': checkin_date,
                    # 'ref': room_name,
                    'team_id': team_vendite.id,
                    'email_utente': email,
                    'telefono_utente': phone,
                    'nome_stanza_utente': roomName,
                    'nota_interna': channelNotes,
                    'stato_del_pagamento': paymentStatus,
                    'tipo_di_pagamento': paymentType,
                    'pulizia_camera': stato_camera,
                    'ultima_pulizia': ultima_pulizia,
                    'tipologia_camera': tipologia_camera,

                })

                # Creazione delle linee della fattura
                linee_fattura = []

                # Linea per il prodotto 1 (Pernotto)
                linea_fattura_pernotto = {
                    'move_id': room_booking_obj.id,
                    'product_id': room_product.id,  # ID del prodotto 'Pernotto' nel portale amministrazione
                    'name': f"Prenotazione {refer} dal {checkin_date} al {checkout_date}",
                    'quantity': 1,
                    'price_unit': roomGross,
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
                         #f"Refer: {refer}<br>"
                         #f"Prezzo totale: {roomGross}<br>"
                         f"Ospiti totali: {totalGuest}<br>"
                         f"Adulti: {totaleadulti}<br>"
                         f"Bambini: {totalChildren}<br>"
                         f"Neonati: {totalInfants}<br>"
                         #f"Checkin: {checkin}<br>"
                         #f"Checkout: {checkout}<br>"
                         f"Numero notti: {n_notti}<br>"
                         f"Nome camera: {tipologia_camera}<br>"
                         f"Note interne: {channelNotes}<br>"
                         f"Stato del pagamento: {paymentStatus} <br>"
                         f"Tipo di pagamento: {paymentType} <br>"                         
                         #f"Quantity soggiorno: {quantity_soggiorno}<br>"
                         #f"Prezzo unitario: {roomGross}<br>"
                         #f"City utente: {city}<br>"
                         f"<p><b><font size='2' face='Arial'>Informazioni cliente</font></b><br>"
                         f"Email: {email}<br>"
                         #f"Guests List: {nome_completo}<br>"
                         f"Telefono: {phone}</pr>",
                         #f"Nome stanza: {roomName}<br>"
                         #f"Pulizia camera:{stato_camera}<br>"
                         #f"Ultima pulizia:{ultima_pulizia}<br>"
                         #f"Piattaforma di prenotazione: {channelName}<br>"
                    message_type='comment'
                )

            return Response(json.dumps(response_data_list), content_type='application/json', status=200)
        else:
            print("Errore nella richiesta API:", response.status_code)
            # In caso di errore, puoi restituire una risposta di errore appropriata
            return Response("Errore nella richiesta API", content_type='text/plain', status=response.status_code)





