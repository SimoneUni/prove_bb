import requests
import json


# Dati del client per ottenere il token
CLIENT_ID = "public_a3a3b3c2278b4deabd9108e74c5e8af2"
CLIENT_SECRET = "secret_47ff49e5533047a994869a012a94eecfTOIUDRGXYK"


# Funzione per ottenere il token di accesso
def get_access_token():
    endpoint = "https://api.octorate.com/connect/rest/v1/identity/apilogin"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(endpoint, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Errore nell'ottenere il token di accesso: {response.status_code} - {response.text}")
        return None


# Ottieni il token di accesso
access_token = get_access_token()
if access_token:
    print(f"Token di accesso ottenuto con successo: {access_token}")
else:
    print("Errore nell'ottenere il token di accesso.")


def get_access_token2():
    endpoint = "https://api.octorate.com/connect/rest/v1/identity/token"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": "3c7611558345463bb4f29455cccb99f54f9a179690584decb36987c167e29886",
        "client_id": CLIENT_ID,  # Assicurati di aver definito CLIENT_ID
        "client_secret": CLIENT_SECRET,  # Assicurati di aver definito CLIENT_SECRET
        "redirect_uri": "https://api.octorate.com/connect/docs/oauth2-redirect.html"
    }

    response = requests.post(endpoint, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Errore nell'ottenere il token di accesso: {response.status_code} - {response.text}")
        return None


# Ottieni il token di accesso
access_token_a = get_access_token2()

if access_token_a:
    print(f"Token per visionare le reservation è : {access_token_a}")
else:
    print("Errore nell'ottenere il token di accesso.")


def refresh_token():
   endpoint = "https://api.octorate.com/connect/rest/v1/identity/refresh"

   headers = {
       "Accept": "application/json",
       "Content-Type": "application/x-www-form-urlencoded"
   }

   payload = {
                "grant_type": "authorization_code",
                "code": "cc4a0b29064f4b36992e1203acdbf613eb0eda5cd36c43bab2c687820d4c8e79",
               "client_id": CLIENT_ID,  # Assicurati di aver definito CLIENT_ID
               "client_secret": CLIENT_SECRET,  # Assicurati di aver definito CLIENT_SECRET
                "redirect_uri": "https://api.octorate.com/connect/docs/oauth2-redirect.html",
                'refresh_token': '2acf003360ea4ebca6871b5d7e56efe2'
   }

   response = requests.post(endpoint, data=payload, headers=headers)

   if response.status_code == 200:
       print("refresh avvenuto con successo")
       return response.json().get("access_token")
   else:
       print(f"Errore nell'ottenere il token di accesso: {response.status_code} - {response.text}")
       return None


def fetch_accommodations(token):
    endpoint = "https://api.octorate.com/connect/rest/v1/accommodation"
    # print(token)

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Errore nell'ottenere gli accommodation: {response.headers}, {headers}")
        return []


# Esempio di utilizzo:
# Ottieni il token di accesso (già ottenuto precedentemente)
access_token = get_access_token()
# Ottenere gli accommodation
accommodations = fetch_accommodations(access_token)
if accommodations:
    print(f"Gli accommodation ottenuti con successo: {accommodations}")
else:
    print("Nessun accommodation disponibile o errore nell'ottenimento.")


def fetch_reservations_for_accommodation_id(access_token_a, accommodation_id):
    reservation_endpoint = f"https://api.octorate.com/connect/rest/v1/reservation/{accommodation_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token_a}"
    }
    response = requests.get(reservation_endpoint, headers=headers)

    if response.status_code == 200:
        reservations = response.json()
        return reservations
    else:
        print(
            f"Errore nell'ottenere le prime prenotazioni per l'alloggio {accommodation_id}, {headers}, {response.status_code}, {response.text}")
        return []


# Esempio di utilizzo:
# Ottieni il token di accesso (già ottenuto precedentemente)

# access_token_a = get_access_token2()
# print(access_token_a)
# Inserisci l'ID dell'alloggio per cui desideri ottenere le prenotazioni
accommodation_id = "632966"

# Ottieni le prenotazioni per l'alloggio selezionato utilizzando il token ottenuto
reservations = fetch_reservations_for_accommodation_id(access_token_a, accommodation_id)

# Controlla se ci sono prenotazioni
if reservations:
    print(f"{accommodation_id}: {reservations}")

    # Converti le prenotazioni in formato JSON
    reservations_json = json.dumps(reservations)

    # Definisci l'URL del webhook al quale inviare le prenotazioni
    webhook_url = "https://webhook.site/e2e61afa-8888-487d-a8d6-4c79156487dd"

    # Invia i dati al webhook
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(webhook_url, data=reservations_json, headers=headers)

    # Verifica la risposta del webhook
    if response.status_code == 200:
        print("Dati inviati con successo al webhook.")
    else:
        print(f"Errore nell'invio dei dati al webhook: {response.status_code} - {response.text}")
else:
    print("Nessuna prenotazione disponibile o errore nell'ottenimento.")

print(f"{accommodation_id}:{reservations}")



def fetch_webhooks(access_token_a):
    endpoint = "https://api.octorate.com/connect/rest/v1/subscription"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token_a}"
    }

    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        print(f"Errore nell'ottenere i webhooks configurati: {response.status_code} - {response.text} - {headers}")
        return []

    return response.json()



#
# def create_subscription(event_type, access_token_a):
#     # URL per il tipo di evento specifico
#     subscription_url = f"https://api.octorate.com/connect/rest/v1/subscription/{event_type}"
#     print(subscription_url)
#     # URL dell'endpoint a cui verranno inviati i webhook
#    # endpoint_url = "https://webhook.site/7562c12d-e21c-402c-8faa-b6c08e9e564d"
#
#     # Crea il payload per la richiesta
#     payload = {
#         "endpoint": webhook_url,
#         #"type": "CONTENT_NOTIFICATION"
#     }
#     print(payload)
#     # Aggiungi l'intestazione di autorizzazione
#     headers = {
#         "Authorization": f"Bearer {access_token_a}",
#         "Content-Type": "application/json"
#     }
#     print(headers)
#     # Invia la richiesta per creare l'abbonamento
#     response = requests.post(subscription_url, json=payload, headers=headers)
#
#     if response.status_code == 200:
#         print(f"Abbonamento per {event_type} creato con successo.")
#     else:
#         print(f"Errore durante la creazione dell'abbonamento per {event_type}: {response.status_code} - {response.text}")
#
# # Assicurati di avere un access token valido
#
#
# # Definisci i tipi di eventi per i quali vuoi creare gli abbonamenti
# event_types = ["RESERVATION_CREATED", "RESERVATION_CHANGE", "RESERVATION_CANCELLED", "RESERVATION_CONFIRMED"]
#
# # Chiamare la funzione per ciascun tipo di evento
# for event_type in event_types:
#     create_subscription(event_type, access_token_a)
#     print("è andata")