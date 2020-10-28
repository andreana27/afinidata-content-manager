from django.contrib.auth.models import User
from articles.models import Demographic
from attributes.models import Attribute
from licences.models import License
from programs.models import Program
from entities.models import Entity
from areas.models import Area
from messenger_users.models import User as MessengerUser
from instances.models import Instance
from django.db import models


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
    programs = models.ManyToManyField(Program)
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
                                                          ('save_values_block', 'Redirect Chatfuel block'),
                                                          ('set_attributes', 'Set attribute'),
                                                          ('user_input', 'Save user input'),
                                                          ('image', 'Send image'),
                                                          ('condition', 'Condition'),
                                                          ('redirect_session', 'Redirect session'),
                                                          ('consume_service', 'Consume service')))

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
    user_id = models.ForeignKey(MessengerUser, on_delete=models.CASCADE, null=True)
    instance_id = models.ForeignKey(Instance, on_delete=models.CASCADE, null=True)
    bot_id = models.IntegerField(default=1)
    type = models.CharField(max_length=255, default='open')
    value = models.IntegerField(default=0, null=True)
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


class UserInput(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    text = models.TextField()
    validation = models.CharField(max_length=50, null=True, choices=(('phone', 'Phone'), ('email', 'Email'),
                                                                     ('date', 'Date')))
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
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


class SetAttribute(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.attribute.name + ':' + self.value


class Condition(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    condition = models.CharField(max_length=50, choices=(('equal', 'Equal'), ('not_equal', 'Not equal'),
                                                         ('in', 'Is in')))
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.attribute.name + ' ' + self.condition + ' ' + self.value


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


class RedirectSession(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session.name


class Service(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service


class FieldProgramExclusion(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FieldProgramComment(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
