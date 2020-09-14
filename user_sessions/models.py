from articles.models import Topic, Demographic
from django.db import models
from areas.models import Area
from etities.models import Entity
from licences.models import License


class SessionType(models.Model):
    name = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=100)
    min = models.IntegerField(null=True, default=0, verbose_name='Min meses')
    max = models.IntegerField(null=True, default=72, verbose_name='Max meses')
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, null=True)
    areas = models.ManyToManyField(Area)
    entities = models.ManyToManyField(Entity)
    licences = models.ManyToManyField(License)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Channels(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    channel_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pk


class Lang(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    language_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pk


class Field(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    field_type = models.CharField(max_length=50, choices=(('text', 'Text'), ('quick_replies', 'Quick Replies'),
                                           ('save_values_block', 'Save Values Block')))

    def __str__(self):
        return "%s" % self.pk


class Interaction(models.Model):
    """
    Tracking the user interaction with the sessions

    Args:
        session:
        user_id: ID del usuario del bot asociado a la interaction.
        username: Username del usuario del bot asociado a la interaction (Redundancia que se utiliza para ciertos reportes).
        channel_id: channel id del usuario del bot.
        bot_id: Bot al cual está conectado el usuario.
        type: String que guarda el tipo de interaction que ejecutó el usuario, estas pueden ser de cualquier tipo. De uso cotidiano en la plataforma en ciertas cosas se encuentran ‘session’ y ‘opened’, su uso puede ser muy variado.
        value: Valor de tipo Entero que puede almacenarse en las interacciones. (Formato de Entero posiblemente temporal, guardado así por alguna necesidad, por revisar)
        created_at, updated_at: (Uso general, fecha de creación, fecha de última actualización).
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True)
    user_id = models.IntegerField(default=0)
    instance_id = models.IntegerField(default=0)
    bot_id = models.IntegerField(default=1)
    type = models.CharField(max_length=255, default='open')
    value = models.IntegerField(default=0)
    text = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type+":"+self.value


class Message(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Reply(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    attribute = models.CharField(max_length=50, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    redirect_block = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class Response(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    instance_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    response = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


class RedirectBlock(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    block = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.block


class DemographicQuestion(models.Model):
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE)
    lang = models.CharField(max_length=10, choices=LANGS, default=LANGS[0][0], verbose_name='idioma')
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class DemographicReply(models.Model):
    demographic = models.ForeignKey(Demographic, on_delete=models.CASCADE)
    lang = models.CharField(max_length=10, choices=LANGS, default=LANGS[0][0], verbose_name='idioma')
    reply = models.TextField()
    value = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reply
