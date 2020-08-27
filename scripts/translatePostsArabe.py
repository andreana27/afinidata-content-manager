# Create WordPress pages with translated content from already existing WordPress pages registered in Post
# We obtain only the plain text from the page to translate, in order to retain unchanged the HTML tags.
from posts.models import PostLocale, Post
import boto3
import json
import base64
import requests
import csv
import time
from bs4 import BeautifulSoup

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
        r = requests.get('https://activities.afinidata.com/wp-json/wp/v2/posts?slug=%s' % (post_slug))
        #get imitating-animal-sounds
        post = None
        try:
            post = r.json()[0]
        except:
            raise Exception(dict(request = 'https://activities.afinidata.com/wp-json/wp/v2/posts?slug=%s' % (post_slug)))
        return post
    def save_post_wordpress(post_slug, post_title, post_content, featured_media=0):
        url_srcdest = "https://activities.afinidata.com/wp-json/wp/v2/posts/"
        code = 'bHVjaTp3TWFLIEIxbFMgTFBDNiBqamFxIHl2UmMgSjEzUwo='
        headers = {'Content-Type': 'application/json',
                 'Authorization': 'Basic %s' % (code),
                 'Username': 'luci',
                 'Password': '%s' % (code)}
        data = \
            {
                "title": post_title,
                "content": post_content,
                "status": "draft",
                "slug": post_slug,
                "featured_media": featured_media
            }
        response = requests.post(url_srcdest, data=json.dumps(data), headers=headers)
        if response.status_code < 199 or response.status_code > 300:
            raise Exception(dict(code=response.status_code, response = response.json(), request = data))
        return 'https://activities.afinidata.com/%s/' % (post_slug)

    #Get the URLs of posts that language_origin matches PostLocale,
    #but have no language_destination PostLocale
    # Get al posts that doesnt have an lenguage_destination translation
    done = Post.objects.filter(postlocale__lang=language_destination)
    excluded_posts = set()
    for d in done:
        excluded_posts.add(d.id)
    post_to_translate = Post.objects.exclude(id__in=excluded_posts) \
        .filter(content__startswith='https://activities.afinidata.com/') \
        .filter(id=625)

    translated_posts = []
    for post in post_to_translate:
        post_name = post.content \
          .replace('https://activities.afinidata.com/', '') \
          .replace('/', '')
        # Get the content from the wordpress API
        wordpress_post = get_post_from_wordpress(post_slug=post_name)
        # Separate text to avoid translating HTML tags, we only need to translate plain text
        text_html = wordpress_post['content']['rendered'].replace("^", "")\
            .replace("<ul>", "<p>").replace("</ul>", "</p>")\
            .replace("<li>", "").replace("</li>", "\n")
        featured_media = wordpress_post['featured_media']
        title = post.name
        delimiter = "^"
        plain_text = title + "" + delimiter + " " +text_html

        # Translate
        translate = boto3.client(service_name='translate', region_name='us-east-2', use_ssl=True)
        # Wait to avoid ThrottlingException
        time.sleep(0)
        plain_text = translate \
            .translate_text(Text=plain_text,
                            SourceLanguageCode=language_origin,
                            TargetLanguageCode=language_destination)['TranslatedText']

        # Join again the plain text with the HTML structure
        title = plain_text.split(delimiter)[0]
        plain_text_array = plain_text.split(delimiter)[1]

        #Create the new translated Wordpress Page, save_new_post_in_wordpress
        url = save_post_wordpress(post_slug=language_destination+'-%s' % (post_name),
                                  post_title=title,
                                  post_content=plain_text_array,
                                  featured_media=featured_media)
        # Use BeautifulSoup to get plain text
        soup = BeautifulSoup(plain_text_array, features="html.parser", from_encoding='utf-8')
        clear_text = soup.get_text()

        # Use BeautifulSoup to extract the summary within the content
        # Obtain the rectangles tag elements
        rectangles = soup.find_all("p", class_="has-background")
        # Get the text from those rectangles
        summary = "\n".join([rectangle.get_text() for rectangle in rectangles])

        #save postLocale
        new_post_locale = PostLocale(lang=language_destination,
                                     locale=locale_destination,
                                     title=title,
                                     rich_post_content=plain_text_array,
                                     plain_post_content=clear_text,
                                     link_post=url,
                                     summary_content=summary,
                                     post_id=post.id)
        new_post_locale.save()
        print("ID:", post.id, "Translated:", title)
        translated_posts.append(dict(post=post.id,
                                     post_locale=new_post_locale.id,
                                     post_name=post.name,
                                     url=url))
    #generate_csv(list=translated_posts, filename = 'output.csv')
    return dict(translated=len(post_to_translate), posts=translated_posts)


translate_locale_posts(language_origin='es', language_destination='ar', locale_destination='ar_EA')
