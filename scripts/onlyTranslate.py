# Create WordPress pages with translated content from already existing WordPress pages registered in Post
# We obtain only the plain text from the page to translate, in order to retain unchanged the HTML tags.
from posts.models import PostLocale, Post
import boto3
import json
import base64
import requests
import csv
import time
import os
"""
Proceso para traducir post del wordpress
Requeridos importantes:
1. Set credenciales para el servicio boto3 de aws en ~/.aws/credentials
2. requerir la url del wordpress
3. requerir username y password para el wordpress
4. idioma original y nuevo idioma
"""
def add(x, y):
    return x + y

def translate_locale_posts(language_origin = 'es',
                           language_destination = 'pt',
                           locale_destination = 'pt_PT'):

    def generate_csv(list, filename):
        keys = list[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(list)

    def get_post_from_wordpress(post_slug):
        import requests
        r = requests.get('https://afinicontent.com/wp-json/wp/v2/posts?slug=%s' % (post_slug))
        #get imitating-animal-sounds
        post = None
        try:
            post = r.json()[0]
        except:
            raise Exception(dict(request = 'https://afinicontent.com/wp-json/wp/v2/posts?slug=%s' % (post_slug)))
        return post

    def save_post_wordpress(post_slug, post_title, post_content):
        user = os.getenv('AFINICONTENT_WP_USER')
        # code = os.getenv('AFINICONTENT_WP_PASS')
        # code = 'bHVjaTp3TWFLIEIxbFMgTFBDNiBqamFxIHl2UmMgSjEzUwo='#str(base64.b64encode(b'luci:wMaK B1lS LPC6 jjaq yvRc J13S'), 'utf-8')
        code = str(base64.b64encode(b'luci:NGV8 3x5L kZ0m QENi qZEA XavL'),'utf-8')

        url_srcdest = "https://afinicontent.com/wp-json/wp/v2/posts/"
        headers = {'Content-Type': 'application/json',
                 'Authorization': 'Basic %s' % (code),
                 'Username': user,
                 'Password': '%s' % (code)}
        data = \
            {
                "title" : post_title,
                "content" : post_content,
                "status" : "draft",
                "slug" : post_slug
            }
        response = requests.post(url_srcdest, data=json.dumps(data), headers=headers)
        if response.status_code < 199 or response.status_code > 300:
            raise Exception(dict(code = response.status_code, response = response.json(), request = data))
        return 'https://afinicontent.com/%s/' % (post_slug)


    # post_to_translate = ['woven-shapes',
    #                      'odd-splash','stick-hunt','orange-smash','balloon-tennis',
    #                      'walk-the-ball','seed-art',
    #                      'nail-the-pumpkin','playdough-noodles','santas-little-helper']

    post_to_translate = [
        'explorando-texturas-2',
        'es-hora-de-agarrar-objetos',
        'bolsa-sensorial-con-vegetales',
        'masajito',
        'botella-de-sonido',
        'y-mi-nombre-es-2',
        'imitando-sonidos-de-animales',
        'y-suena-asi',
        'te-quiero-chiquitin',
        'ojos-traviesos',
        'deja-caer-el-pom-pon',
        'reconocimiento-visual',
        'a-bailar',
        'platicando-con-papi-y-mami',
        'miralo-hablale-y-reacciona-2',
        'mis-primeros-cuentos',
        'peluches-voladores',
        'remando-en-bote',
        'bebe-artista',
        'tarjetas-en-blanco-y-negro',
        'pintura-comestible',
        'avioncito-bebe',
        'la-hora-de-relajacion',
        'reacciones-circulares-primarias',
        'combinaciones-mentales'
    ]

    for post in post_to_translate:
        post_name = post
        # Get the content from the wordpress API
        wordpress_post = get_post_from_wordpress(post_slug = post_name)
        # Separate text to avoid translating HTML tags, we only need to translate plain text
        text_html = " " + wordpress_post['content']['rendered'].replace("^", "")
        delimiter = "^"
        tags_array = []
        plain_text_array = []
        i = 0
        while i < len(text_html):
            text = ""
            while i < len(text_html) and text_html[i] != "<":
                text += text_html[i]
                i += 1
            plain_text_array.append(text)
            tag = ""
            while i < len(text_html) and text_html[i] != ">":
                tag += text_html[i]
                i += 1
            if i < len(text_html):
                tag += text_html[i]
                i += 1
            tags_array.append(tag)

        plain_text = (" "+delimiter+" ").join(plain_text_array)

        # Translate
        translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)
        # Wait to avoid ThrottlingException
        time.sleep(20)
        plain_text = translate \
            .translate_text(Text=plain_text,
                            SourceLanguageCode=language_origin,
                            TargetLanguageCode=language_destination)['TranslatedText']

        # Join again the plain text with the HTML structure
        plain_text_array = plain_text.split(delimiter)

        translated_text_html = ""
        for i in range(len(plain_text_array)):
            if i < len(plain_text_array):
                translated_text_html += plain_text_array[i]
            if i < len(tags_array):
                translated_text_html += tags_array[i]

        #Create the new translated Wordpress Page, save_new_post_in_wordpress
        url = save_post_wordpress(post_slug = language_destination+'-%s' % (post_name),
                                  post_title=post_name,
                                  post_content = translated_text_html)
        print("Translated:", url)
    return True

translate_locale_posts(language_origin='es', language_destination='pt', locale_destination = 'pt_PT')
