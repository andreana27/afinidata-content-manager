import pandas as pd
from posts.models import Taxonomy, Post, Area, Subarea, Componente, Materiales, Situacional
from posts.models import QuestionResponse, Question
# pip install --upgrade pandas
# pip install --upgrade xlrd
# sudo pip3 install xlrd

doc = pd.read_excel('cargaPosts.xlsx')
# Preview the first 5 lines of the loaded data
data = pd.DataFrame(data=doc)
# print(data.head)
# print(len(data))
# len(data)
TIEMPO_DURACION = [
    (5, '5 minutos'),
    (10, '10 minutos'),
    (15, '15 minutos'),
    (20, '20 minutos'),
    (25, '25 minutos'),
    (30, '30 minutos'),
    (40, 'Más de 30 minutos')
]

TAG_PREPARACION =[
    ('baja', 'Preparación baja'),
    ('media', 'Preparación media'),
    ('alta', 'Preparación alta')
]

TAG_MATERIALES =[
    ('pocos', 'Pocos materiales'),
    ('algunos', 'Algunos materiales'),
    ('muchos', 'Muchos materiales')
]

TAG_INTEGRANTES =[
    (0, 'En grupo'),
    (1, 'Individual')
]


def get_id(list, value, default):
    for l in list:
        if value == l[1]:
            return l[0]
    return default


for i in range(len(data)):
    # Crear Post
    new_post = Post(
        name=data.loc[i, "NOMBRE"],
        content=data.loc[i, "Content"],
        min_range=data.loc[i, "Min range"],
        max_range=data.loc[i, "Max range"],
        thumbnail=data.loc[i, "Thumbnail"],
        tiempo_duracion=get_id(TIEMPO_DURACION, data.loc[i, "TIEMPO APROX. DE DURACIÓN"], 40),
        preparacion=get_id(TAG_PREPARACION, data.loc[i, "TAG DE PREPARACIÓN"], 'media'),
        cantidad_materiales=get_id(TAG_MATERIALES, data.loc[i, "TAG DE MATERIALES"], 'algunos'),
        integrantes=get_id(TAG_INTEGRANTES, data.loc[i, "TAG INTEGRANTES"], 1)
    )
    new_post.save()
    # Agregar tipos de materiales
    if not pd.isnull(data.loc[i, "TIPO DE MATERIALES"]):
        m = Materiales.objects.filter(name=data.loc[i, "TIPO DE MATERIALES"]).first()
        new_post.materiales.add(m)
    if not pd.isnull(data.loc[i, "TIPO DE MATERIALES 2"]):
        m = Materiales.objects.filter(name=data.loc[i, "TIPO DE MATERIALES 2"]).first()
        new_post.materiales.add(m)
    if not pd.isnull(data.loc[i, "TIPO DE MATERIALES 3"]):
        m = Materiales.objects.filter(name=data.loc[i, "TIPO DE MATERIALES 3"]).first()
        new_post.materiales.add(m)
    # Agregar tag situacionales
    if not pd.isnull(data.loc[i, "TAG SITUACIONAL"]):
        s = Situacional.objects.filter(name=data.loc[i, "TAG SITUACIONAL"]).first()
        new_post.situacional.add(s)
    if not pd.isnull(data.loc[i, "TAG SITUACIONAL 2"]):
        s = Situacional.objects.filter(name=data.loc[i, "TAG SITUACIONAL 2"]).first()
        new_post.situacional.add(s)

    # Crear pregunta
    new_question = Question(
        name=data.loc[i, "PREGUNTA"],
        lang="es",
        post=new_post,
        replies=data.loc[i, "Respuesta 0"]+', '+data.loc[i, "Respuesta 1"]+', '+data.loc[i, "Respuesta 2"]+', '+data.loc[i, "Respuesta 3"]+', '+data.loc[i, "Respuesta 4"]
    )
    new_question.save()

    # Crear respuestas
    qr0 = QuestionResponse(question=new_question, response=data.loc[i, "Respuesta 0"], value=data.loc[i, "Valor 0"])
    qr0.save()
    qr1 = QuestionResponse(question=new_question, response=data.loc[i, "Respuesta 1"], value=data.loc[i, "Valor 1"])
    qr1.save()
    qr2 = QuestionResponse(question=new_question, response=data.loc[i, "Respuesta 2"], value=data.loc[i, "Valor 2"])
    qr2.save()
    qr3 = QuestionResponse(question=new_question, response=data.loc[i, "Respuesta 3"], value=data.loc[i, "Valor 3"])
    qr3.save()
    qr4 = QuestionResponse(question=new_question, response=data.loc[i, "Respuesta 4"], value=data.loc[i, "Valor 4"])
    qr4.save()

    # Crear taxonomia
    new_taxonomy = Taxonomy(
        post=new_post,
        area=Area.objects.filter(name=data.loc[i, "ÁREA"]).first(),
        subarea=Subarea.objects.filter(name=data.loc[i, "SUB-ÁREA"]).first(),
        component=Componente.objects.filter(name=data.loc[i, "COMPONENTE"]).first()
    )
    new_taxonomy.save()
    print(data.loc[i, "NOMBRE"])

