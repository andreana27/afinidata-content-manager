# Create WordPress pages with translated content from already existing WordPress pages registered in Post
# We obtain only the plain text from the page to translate, in order to retain unchanged the HTML tags.
from posts.models import PostLocale, Post
import boto3
import json
import base64
import requests
import csv
import time

AFINICONTENT_URL = "https://afinicontent.com"

def add(x, y):
    return x + y

def translate_locale_posts(language_origin = 'es',
                           language_destination = 'en',
                           locale_destination = 'en_US'):

    def generate_csv(list, filename):
        keys = list[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(list)

    def get_post_from_wordpress(post_slug):
        import requests
        r = requests.get('%s/wp-json/wp/v2/posts?slug=%s' % (AFINICONTENT_URL, post_slug))
        #get imitating-animal-sounds
        post = None
        try:
            post = r.json()[0]
        except:
            raise Exception(dict(request = '%s/wp-json/wp/v2/posts?slug=%s' % (AFINICONTENT_URL, post_slug)))
        return post

    def save_post_wordpress(post_slug, post_title, post_content, featured_media):
        url_srcdest = AFINICONTENT_URL + "/wp-json/wp/v2/posts/"
        # code = 'bHVjaTp3TWFLIEIxbFMgTFBDNiBqamFxIHl2UmMgSjEzUwo='#str(base64.b64encode(b'luci:wMaK B1lS LPC6 jjaq yvRc J13S'), 'utf-8')

        code = str(base64.b64encode(b'luci:NGV8 3x5L kZ0m QENi qZEA XavL'),'utf-8')

        headers = {'Content-Type': 'application/json',
                 'Authorization': 'Basic %s' % (code),
                 'Username': 'luci',
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

        return '%s/%s/' % (AFINICONTENT_URL, post_slug)

    #Get the URLs of posts that language_origin matches PostLocale,
    #but have no language_destination PostLocale
    done = PostLocale.objects.filter(lang=language_destination)
    excluded_posts = set()

    for d in done:
        excluded_posts.add(d.post)

    post_locales_to_translate = PostLocale.objects \
      .exclude(post__in=excluded_posts) \
      .filter(lang = language_origin)

    # Get al posts that doesnt have an lenguage_destination translation
    done = Post.objects.filter(postlocale__lang=language_destination)
    excluded_posts = set()

    for d in done:
        excluded_posts.add(d.id)

    post_to_translate = Post.objects.exclude(id__in=excluded_posts) \
        .filter(content__startswith=AFINICONTENT_URL)[:2]

    translated_posts = []

    for post in post_to_translate:
        post_name = post.content \
          .replace(AFINICONTENT_URL+'/', '') \
          .replace('/', '')

        # Get the content from the wordpress API
        wordpress_post = get_post_from_wordpress(post_slug = post_name)

        # Separate text to avoid translating HTML tags, we only need to translate plain text
        text_html = " " + wordpress_post['content']['rendered'].replace("^", "")
        title = post.name
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

        plain_text = title + delimiter + (" "+delimiter+" ").join(plain_text_array)

        # Translate
        translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)

        # Wait to avoid ThrottlingException
        time.sleep(20)

        plain_text = translate \
            .translate_text(Text=plain_text,
                            SourceLanguageCode=language_origin,
                            TargetLanguageCode=language_destination)['TranslatedText']

        # Join again the plain text with the HTML structure
        title = plain_text.split(delimiter)[0]
        plain_text_array = plain_text.split(delimiter)[1:]

        translated_text_html = ""

        for i in range(len(plain_text_array)):
            if i < len(plain_text_array):
                translated_text_html += plain_text_array[i]
            if i < len(tags_array):
                translated_text_html += tags_array[i]

        #Create the new translated Wordpress Page, save_new_post_in_wordpress
        url = save_post_wordpress(post_slug = language_destination+'-%s' % (post_name),
                                  post_title = title,
                                  post_content = translated_text_html,
                                  featured_media=wordpress_post['featured_media'])
        #save postLocale
        new_post_locale = PostLocale(lang=language_destination,
                                   locale=locale_destination,
                                   title=title,
                                   plain_post_content=translated_text_html,
                                   link_post=url,
                                   post_id=post.id)
        new_post_locale.save()

        print("ID:", post.id, "Translated:", title, "Image:")

        translated_posts.append(dict(post = post.id,
                                     post_locale=new_post_locale.id,
                                     post_name = post.name,
                                     url = url))

        generate_csv(list = translated_posts, filename = 'output.csv')

    return dict(translated = len(post_to_translate), posts = translated_posts)


translate_locale_posts(language_origin='en', language_destination='pt', locale_destination = 'pt_PT')
