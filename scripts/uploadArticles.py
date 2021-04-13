from articles.models import Article
from user_sessions.models import SessionType
from topics.models import Topic
from programs.models import Program
import pandas as pd
import requests
from bs4 import BeautifulSoup


doc = pd.read_excel('cargaArticulos.xlsx')
# Preview the first 5 lines of the loaded data
data = pd.DataFrame(data=doc)


def get_post_from_wordpress(post_slug):
    r = requests.get('https://afinicontent.com/wp-json/wp/v2/article?slug=%s' % post_slug)
    post = None
    try:
        post = r.json()[0]
        r = requests.get('https://afinicontent.com/wp-json/wp/v2/media/%s' % post['featured_media'])
        post['thumbnail'] = r.json()['guid']['rendered']
    except:
        raise Exception(dict(request='https://afinicontent.com/wp-json/wp/v2/article?slug=%s' % post_slug))
    return post


for i in range(len(data)):
    type, created = SessionType.objects.get_or_create(name=data.loc[i, "TYPE"])
    content = data.loc[i, "CONTENT"]
    topic, created = Topic.objects.get_or_create(name=data.loc[i, "TOPIC"])
    post_slug = data.loc[i, "CONTENT"].split('/')[-2]
    wordpress_post = get_post_from_wordpress(post_slug)
    soup = BeautifulSoup(wordpress_post['content']['rendered'].replace("<li>", "- ").replace("</li>", "\n"),
                         features="html.parser")
    text_content = soup.get_text()
    thumbnail = wordpress_post['thumbnail']
    article = Article.objects.filter(name=data.loc[i, "NAME"])
    if article.exists():
        article = article.last()
        article.name = data.loc[i, "NAME"]
        article.status = 'published'
        article.type = type
        article.content = content
        article.text_content = text_content
        article.min = int(data.loc[i, "MIN"])
        article.max = int(data.loc[i, "MAX"])
        article.preview = data.loc[i, "PREVIEW"]
        article.thumbnail = thumbnail
        article.topics.add(topic)
        for program_name in data.loc[i, "PROGRAMS"].split(', '):
            program = Program.objects.filter(name=program_name)
            if program.exists():
                program = program.last()
                article.programs.add(program)
        article.save()
        print(article.id, article.name, "(EDITED)")
    else:
        new_article = Article(name=data.loc[i, "NAME"],
                              status='published',
                              type=type,
                              content=content,
                              text_content=text_content,
                              min=int(data.loc[i, "MIN"]),
                              max=int(data.loc[i, "MAX"]),
                              preview=data.loc[i, "PREVIEW"],
                              thumbnail=thumbnail)
        new_article.save()
        new_article.topics.add(topic)
        for program_name in data.loc[i, "PROGRAMS"].split(', '):
            program = Program.objects.filter(name=program_name)
            if program.exists():
                program = program.last()
                new_article.programs.add(program)
        print(new_article.id, new_article.name)
