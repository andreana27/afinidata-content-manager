'''
Copy paste this script in a django shell:
    1. Activate venv (source venv/bin/activate)
    2. Install boto3 (pip install -r requirements.txt)
    3. Save the following https://nextcloud.afinidata.com/index.php/apps/files/?dir=/Credenciales&fileid=241# file to ~/.aws/credentials
    4. Start the shell & python manage.py Copy Paste script
    5. See result
'''
from reply_repo.models import Message
from posts.models import Question
from celery import shared_task
import boto3

@shared_task
def add(x, y):
    return x + y

@shared_task
def translate_reply_repo(language_origin = 'es', language_destination = 'en', destination_locale = 'en_US'):
    translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)

    done = Message.objects.filter(language=language_destination)
    excluded = set()
    for d in done:
        if d.id:
            excluded.add(d.block_id)

    messages_to_translate = Message.objects \
      .exclude(block_id__in=excluded) \
      .filter(
        language = language_origin)

    for message in messages_to_translate:
      result = translate.translate_text(Text=message.content,
                                        SourceLanguageCode=language_origin,
                                        TargetLanguageCode=language_destination)
      msg_to_save = Message(block_id = message.block_id,
                            state = 'AutoTranslated',
                            language = language_destination,
                            full_locale = destination_locale,
                            content = result.get('TranslatedText'),
                            extra_items = message.extra_items)
      msg_to_save.save()

    return dict(translated = len(messages_to_translate))

def translate_questions(language_origin = 'es', language_destination = 'en', destination_locale = 'en_US'):
    translate = boto3.client(service_name ='translate', region_name = 'us-east-2', use_ssl = True)

    questions_to_translate = Question.objects \
                            .filter(lang = language_origin)

    for question in questions_to_translate:
      name_result = translate.translate_text(Text=question.name,
                                             SourceLanguageCode=language_origin,
                                             TargetLanguageCode=language_destination)
      replies_result = translate.translate_text(Text=question.replies,
                                             SourceLanguageCode=language_origin,
                                             TargetLanguageCode=language_destination)
      q = Question(name = name_result.get('TranslatedText'),
                   lang = language_destination,
                   post = question.post,
                   replies = replies_result.get('TranslatedText'))
      q.save()
    return dict(translated_questions = len(questions_to_translate))

def change_state(language = 'en', desired_state = 'Published'):
    messages_updated = Message.objects \
      .exclude(
        state = desired_state
      ) \
      .filter(
        language = language
      ).update(state=desired_state)
    return dict(updated_messages = len(messages_updated))
