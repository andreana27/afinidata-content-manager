#!/bin/python
'''
Copy paste this script in a django shell:
    1. Activate venv (source venv/bin/activate)
    2. Install boto3 (pip install -r requirements.txt)
    3. Save the following https://nextcloud.afinidata.com/index.php/apps/files/?dir=/Credenciales&fileid=241# file to ~/.aws/credentials
    4. Copy Paste script
    5. See result
'''
from reply_repo import models
import boto3

translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)

done = models.Message.objects.filter(language='en')
excluded = set()
for d in done:
    if d.id:
        excluded.add(d.block_id)

messages_to_translate = models.Message.objects \
  .exclude(block_id__in=excluded) \
  .filter(
    language = 'es')

for message in messages_to_translate:
  result = translate.translate_text(Text=message.content,
              SourceLanguageCode="es", TargetLanguageCode="en")
  msg_to_save = models.Message(block_id = message.block_id,
                               language = 'en',
                               full_locale = 'en_US',
                               content = result.get('TranslatedText'),
                               extra_items = message.extra_items)
  msg_to_save.save()

print (len(messages_to_translate))
