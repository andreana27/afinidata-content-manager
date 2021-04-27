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

def translate_locale_posts(language_origin = 'en',
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

    def save_post_wordpress(post_slug, post_title, post_content, featured_media=""):
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
                "slug" : post_slug,
                "featured_media":featured_media
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
        'lets-play-in-the-sand',
        'colourful-paper-balls',
        'pasta-tower-2',
        'bread-balls',
        'lets-build-with-seeds',
        'vegetable-maze',
        'the-traffic-light',
        'looking-for-elenas-buttons',
        'sand-treasure-hunt',
        'cheese-shapes',
        'the-rainbow-box',
        'emotions-detective',
        'the-emotions-dice',
        'marbled-paper',
        'happiness-and-learning-with-chocolate',
        'this-is-what-the-story-says',
        'temper-tantrums',
        'reaching-the-stars',
        'puzzle-sandwiches',
        'we-spill-water',
        'octopus-sausage',
        'dogs-kisses',
        'the-secret-box',
        'the-corn-harvest',
        'bedtime-stories',
        'learning-the-names-and-colors-of-vegetables',
        's-is-for-sugar',
        'tertiary-circular-reactions',
        'drawing-a-future-together',
        'practicing-with-the-hand-tweezers',
        'blowing-bubbles',
        'my-friends-the-puppets',
        'painting-with-water',
        'looking-for-animals',
        'feeding-the-lion',
        'trolleys-and-tires',
        'guess-the-animal',
        'painting-and-washing-toys',
        'creating-sounds-2',
        'talking-to-the-mirror',
        'pushing-and-walking',
        'where-are-they',
        'sticky-road',
        'tell-me-a-story',
        'creating-a-monster',
        'lets-imitate-the-animals',
        'lets-play-doctor',
        'vegetable-tool',
        'spaghetti-pool',
        'composer-of-emotions',
        'tell-a-story',
        'we-are-writers',
        'i-imitate-scenes-from-my-favorite-story',
        'the-use-of-symbols',
        'comprehension-of-cause-and-effect',
        'ability-to-sort',
        'number-understanding',
        'inability-to-distinguish-appearance-from-reality',
        'sensory-box',
        'tummy-time',
        'lets-fly',
        'lets-exercise-my-little-body-2',
        'sticking-sticks',
        'watering-the-plants',
        'the-jar-of-peacefulness',
        'open-and-close-locks',
        'sewing',
        'bag-of-mysteries',
        'lets-play-with-the-numbers',
        'jars-of-smells',
        'lets-find',
        'hanging-up-clothes',
        'transferring-grains',
        'line-exercises',
        'the-silent-exercise',
        'tracing-lines',
        'knowing-my-babys-reflexes',
        'picasso-on-the-track',
        'creating-art-with-bubbles',
        'knowing-myself',
        'anti-gravity-galaxy',
        'lets-play-with-water',
        'creating-with-nature',
        'cotton-ball-race',
        'lets-speed-up-our-memory',
        'painting-with-leaves',
        'creating-and-differentiating-silhouettes',
        'hide-and-seek-with-sounds',
        'im-a-balloon',
        'fishing',
        'the-manolita-turtle-and-its-shell',
        'colorful-little-feet',
        'my-music-band',
        'playing-with-my-name',
        'colored-ice-art',
        'lets-play-with-snow',
        'lets-sort-stones',
        'little-painters',
        'lets-milk-the-cow',
        'balancing-my-body',
        'secret-bottles',
        'explosive-eggs',
        'lets-follow-the-path',
        'discovering-the-colors',
        'colorful-stamps',
        'my-fingers-can-talk',
        'which-object-is-missing',
        'cardboard-ice-cream',
        'lets-sort',
        'we-are-writers-2',
        'fair-games',
        'im-already-big-and-i-can-do-it-by-myself',
        'what-figure-follows',
        'imitating-daddy-and-mommy',
        'picnic',
        'tunnel-travel',
        'lets-meet-animals-and-plants',
        'lets-play-with-the-cubes',
        'lets-move-our-fingers',
        'head-and-face',
        'learning-textures',
        'ups-and-downs',
        'organizing-pompoms',
        'swimming-in-the-ocean',
        'are-the-pirates-ready-lets-search-for-treasure',
        'what-does-the-baby-like-to-do',
        'imagine-and-create-our-first-story',
        'my-first-ball',
        'from-one-side-to-the-other',
        'spinning',
        'imitating-you',
        'gripping',
        'patting-hands',
        'turn-around',
        'little-worm',
        'my-bath-toys-2',
        'lets-get-painting',
        'hide-and-seek',
        'push-and-pull-the-baby-cart',
        'crawling-together',
        'hats',
        'little-buzzes',
        'happy-feet',
        'i-got-you',
        'my-little-face',
        'a-little-face-in-the-hand',
        'noisy-little-feet',
        'mirror-mirror-on-the-wall',
        'musical-mouth',
        'blow-with-the-pinwheel',
        'musical-baby',
        'play-in-the-labyrinth',
        'here-i-am',
        'lets-score-together',
        'a-star-on-the-tummy',
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
        time.sleep(5)
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
        url = save_post_wordpress(post_slug=language_destination+'-%s' % (post_name),
                                  post_title=post_name,
                                  post_content=translated_text_html,
                                  featured_media=wordpress_post['featured_media'])
        print("Translated:", url)
    return True

translate_locale_posts(language_origin='en', language_destination='pt', locale_destination = 'pt_PT')
