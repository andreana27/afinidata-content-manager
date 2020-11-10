# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
import pandas as pd
import time

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'ACbda6fa352e24722576a2b012612b10fa'
auth_token = '885c161ed1f5f87d34cacdd9988c7461'
client = Client(account_sid, auth_token)
from_phone_number = '+13142549024'
country_code = 'PE'
body = 'El MINISTERIO DE SALUD, UNICEF y AFINI, te invitan GRATIS a recibir actividades para tus hijos. ' \
       'Haz click en el link m.me/afinidatatutor?ref=peru_lima_norte4'
sendMessages = False

# Load spreadsheet
df = pd.read_excel('telefonos.xlsx', sheet_name='Hoja1', skiprows=0)
pd.set_option('mode.chained_assignment', None)
df['IsValid'] = ['' for x in range(len(df['TELEFONO']))]
df['PhoneNumber'] = ['' for x in range(len(df['TELEFONO']))]
df['Type'] = ['' for x in range(len(df['TELEFONO']))]
if sendMessages:
    df['MessageID'] = ['' for x in range(len(df['TELEFONO']))]

sent_count = 0

# Read each row and send message if valid
for i in range(len(df['TELEFONO'])):
    print(i)
    raw_phone_number = df['TELEFONO'][i]
    # Check if phone number is valid and get type
    try:
        # Validate phone number
        phone_number = client.lookups.phone_numbers(raw_phone_number).fetch(country_code=country_code)
        to_phone_number = phone_number.phone_number
        df['IsValid'][i] = 'True'
        df['PhoneNumber'][i] = to_phone_number

        # Get Type: specifies whether the phone is a land line, mobile, or voip phone
        number_type = client.lookups.phone_numbers(to_phone_number).fetch(type=['carrier']).carrier['type']
        df['Type'][i] = number_type

        if sendMessages:
            # Send message
            message = client.messages.create(body=body, from_=from_phone_number, to=to_phone_number)
            df['MessageID'][i] = message.sid
            sent_count = sent_count + 1

            # Only 10 messages per second can be send
            time.sleep(.1)
    except:
        df['IsValid'][i] = 'False'

# Save spreadsheet
df.to_excel('telefonosValidos.xlsx')
print("Finished, sent ", sent_count, " out of ", len(df))