# Requires: pip install BeautifulSoup4
# Copy the text from a WordPress page to the Content Manager into an existing register of PostLocale
# Assumptions: The summary line is contained in the first rectangle, i.e a <p> tag with class property 'has-background'
# Here is a query to check those posts with multiple rectangles or no rectangles
"""
select (length(lower(plain_post_content)) - length(replace(lower(plain_post_content), 'has-background', '')))/length('has-background') as 'count',
    posts_postlocale.*
from posts_postlocale
where lang = 'en'
    and id > 508
having (length(lower(plain_post_content)) - length(replace(lower(plain_post_content), 'has-background', '')))/length('has-background') != 1
order by count asc
"""
# It wasn't doable to search by the phrase 'experience', since there are some posts with its summary
# not adjacent to the phrase 'Learning experience:'
from posts.models import PostLocale, Post
from bs4 import BeautifulSoup
import json


def get_post_from_wordpress(post_slug):
    import requests
    url_srcdest = 'https://activities.afinidata.com/wp-json/wp/v2/posts'
    user = 'estuar.diaz'
    password = '28rS Y9U3 z51d I1E3 0Fng zTsY'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Basic %s' % (password),
               'Username': 'estuar.diaz',
               'Password': '%s' % (password)}
    data = {
        'slug': post_slug,
        'status': 'draft'
        }
    r = requests.get(url_srcdest, data=json.dumps(data), headers=headers, auth=(user, password))
    post = None
    try:
        post = r.json()[0]
    except:
        data = \
            {
                "slug": post_slug,
                "status": "publish"
            }
        r = requests.get(url_srcdest, data=json.dumps(data), headers=headers, auth=(user, password))
        try:
            post = r.json()[0]
        except:
            raise Exception(dict(slug=post_slug, request=r.json()))
    return post


def wordpresstopostlocale(language):
    ids = [680,733,734,735,736,737,738,739,740,741,742,743,744,746,747,748,749,750,757,758,766,769,770,771,772,773,775,
           779,780,801,802,803,804,805,806,846,847,848,849,850,
           851,852,853,854,855,856,857,858,859,860,861,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,
           1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,
           1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,
           1061,1062,963,964,965,966,968,969,970,972,973,974,975,976,979,980,981,982,983,984,985,986,987,988,
           989,990,991,992,993,994,995,996,997,998,999,1000,1002,1003,1004,1006,1007,1008,1009,1010,1011,1103,
           1105,1106,1107,1108,1109,1112,1114,1116,1117,1118,1119,
           1120,1121,1122,1123,1124,1125,1126,1127,1151,1152,1154,1156,1158,1160,1161,1162,1163,1164,1165,1166,
           1167,1168,1171,1172,1173,1174,1175,913,914,915,916,917,918,919,920,921,922,923,924,925,926,927,928,929,
           930,931,932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,
           957,958,959,960,961,962]
    posts_locales = PostLocale.objects.filter(lang=language).filter(id__in=ids)
    for post_locale in posts_locales:
        post_name = post_locale.link_post \
            .replace('https://activities.afinidata.com/', '') \
            .replace('/', '')
        # Get the content from the wordpress API
        wordpress_post = get_post_from_wordpress(post_slug=post_name)
        text_html = wordpress_post['content']['rendered']

        # Use BeautifulSoup to get plain text
        soup = BeautifulSoup(text_html, features="html.parser")
        clear_text = soup.get_text()

        # Use BeautifulSoup to extract the summary within the content
        # Obtain the rectangles tag elements
        rectangles = soup.find_all("p", class_="has-background")
        # Get the text from those rectangles
        summary = "\n".join([rectangle.get_text() for rectangle in rectangles])

        # Update the post locale register
        post_locale.rich_post_content = text_html
        post_locale.plain_post_content = clear_text
        post_locale.summary_content = summary
        post_locale.save()
        print("ID:", post_locale.id, "Title:", post_locale.title)
    print("Total:", len(posts_locales))


def wordpresstopost():
    posts = Post.objects.filter(id__gte=965).filter(id__lte=1139)
    for post in posts:
        post_name = post.content \
            .replace('https://activities.afinidata.com/', '') \
            .replace('/', '')
        # Get the content from the wordpress API
        wordpress_post = get_post_from_wordpress(post_slug=post_name)
        text_html = wordpress_post['content']['rendered']

        # Use BeautifulSoup to get plain text
        soup = BeautifulSoup(text_html, features="html.parser")
        clear_text = soup.get_text()

        # Use BeautifulSoup to extract the summary within the content
        # Obtain the rectangles tag elements
        rectangles = soup.find_all("p", class_="has-background")
        # Get the text from those rectangles
        summary = "\n".join([rectangle.get_text() for rectangle in rectangles])

        # Update the post locale register
        post.content_activity = clear_text
        post.preview = summary
        post.save()
        print("ID:", post.id, "Title:", post.name)


wordpresstopostlocale('en')
# wordpresstopost()
