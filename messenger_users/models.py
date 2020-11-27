import uuid
from django.db import models
from transitions import Machine
from django.db.models.signals import post_init
from django.dispatch import receiver
from instances.models import Instance
from licences.models import License
from entities.models import Entity
from languages.models import Language
from attributes.models import Attribute


class User(models.Model):
    '''
    Describes users as we see them inside the messenger_users app.

    >>> User(1,1,"back", username="test")
    <User: User 1 with m_id: 1; username = test>
    '''
    last_channel_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    channel_id = models.CharField(max_length=50, null=True, unique=True)
    backup_key = models.CharField(max_length=50, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_id = models.IntegerField(default=1)
    username = models.CharField(max_length=100, null=True, unique=True)
    license = models.ForeignKey(License, on_delete=models.DO_NOTHING, null=True)
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING, null=True)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'messenger_users'

    def get_language(self):
        ls = self.userdata_set.filter(data_key='language')
        print(ls)
        if not ls.exists():
            return 'es'
        return ls.last().data_value

    def get_instances(self):
        return Instance.objects.filter(instanceassociationuser__user_id=self.pk)


class UserData(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True, blank=True)
    data_key = models.CharField(max_length=50, null=True, blank=True)
    data_value = models.TextField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.data_value

    class Meta:
        app_label = 'messenger_users'


class Child(models.Model):
    parent_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50)
    dob = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'messenger_users'


class ChildData(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    data_key = models.CharField(max_length=50)
    data_value = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messenger_users'


class Referral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_shared = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='shared_ref')
    user_opened = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='opened_ref', null=True)
    ref_type = models.CharField(choices=[("link", "link"), ("ref","ref")], default="link", max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messenger_users'

    def __str__(self):
        return "User '{}' referred '{}'".format(self.user_shared, self.user_opened)


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    initial_state = models.CharField(max_length=25)
    final_state = models.CharField(max_length=25)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)


def track_activity(*args, **kwargs):
    print(args)
    print(kwargs)
    pass


class UserActivity(models.Model):

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'messenger_users'

    PRE_REGISTER = 'pre_register'
    IN_REGISTRATION = 'in_registration'
    USER_DEAD = 'user_dead'
    WAIT = 'wait'
    USER_QUERY = 'user_query'
    BROADCAST_START= 'broadcast_start'
    TIMED_START = 'timed_start'
    ACTIVE_SESSION = 'active_session'
    PRE_CHURN = 'pre_churn'
    DISPATCHED = 'dispatched'
    OPENED = 'opened'
    FOLLOW_UP = 'follow_up'

    ## Transition consts
    START_REGISTER = 'start_register'
    FINISH_REGISTER = 'finish_register'
    USER_DIE = 'decay'
    RECEIVE_USER_MESSAGE = 'receive_user_message'
    SEND_BROADCAST = 'send_broadcast'
    AWAITED_ENOUGH = 'awaited_enough'
    WANT_ACTIVITY = 'want_activity'
    GET_POST = 'get_post'
    SET_PRE_CHURN = 'set_pre_churn'
    OPEN_POST = 'open_post'
    NO_OPEN = 'no_open'
    GIVE_FEEDBACK = 'give_feedback'
    END_FEEDBACK = 'end_feedback'
    NO_FEEDBACK = 'no_feedback'

    STATE_TYPES = [
        (PRE_REGISTER, PRE_REGISTER),
        (IN_REGISTRATION, IN_REGISTRATION),
        (USER_DEAD, USER_DEAD),
        (WAIT, WAIT),
        (USER_QUERY, USER_QUERY),
        (BROADCAST_START, BROADCAST_START),
        (TIMED_START, TIMED_START),
        (ACTIVE_SESSION, ACTIVE_SESSION),
        (PRE_CHURN, PRE_CHURN),
        (DISPATCHED, DISPATCHED),
        (OPENED, OPENED),
        (FOLLOW_UP, FOLLOW_UP),
    ]

    TRANSITIONS = [
        # TODO: fill
    ]

    state = models.CharField(
        "state",
        max_length=100,
        choices=STATE_TYPES,
        default=WAIT,
        help_text='stado',
    )

    last_change = models.DateTimeField(auto_now=True)

    def on_enter_active_session(self, **kwargs):
        pass


@receiver(post_init, sender=UserActivity)
def init_state_machine(instance, **kwargs):
    states = [state for state, _ in instance.STATE_TYPES]
    machine = instance.machine = Machine(model=instance, states=states, initial=instance.WAIT, \
                                         ignore_invalid_triggers=True, prepare_event=track_activity)
    machine.add_transition(UserActivity.START_REGISTER, UserActivity.PRE_REGISTER, UserActivity.IN_REGISTRATION)
    machine.add_transition(UserActivity.FINISH_REGISTER, UserActivity.IN_REGISTRATION, UserActivity.ACTIVE_SESSION)
    machine.add_transition(UserActivity.USER_DIE, UserActivity.START_REGISTER, UserActivity.USER_DEAD)
    machine.add_transition(UserActivity.USER_DIE, '*', UserActivity.USER_DEAD)

    machine.add_transition(UserActivity.RECEIVE_USER_MESSAGE, UserActivity.WAIT, UserActivity.USER_QUERY)
    machine.add_transition(UserActivity.SEND_BROADCAST, UserActivity.WAIT, UserActivity.BROADCAST_START)
    machine.add_transition(UserActivity.AWAITED_ENOUGH, UserActivity.WAIT, UserActivity.TIMED_START)
    machine.add_transition(UserActivity.WANT_ACTIVITY, UserActivity.USER_QUERY, UserActivity.ACTIVE_SESSION)
    machine.add_transition(UserActivity.WANT_ACTIVITY, UserActivity.BROADCAST_START, UserActivity.ACTIVE_SESSION)
    machine.add_transition(UserActivity.WANT_ACTIVITY, UserActivity.TIMED_START, UserActivity.ACTIVE_SESSION)
    machine.add_transition(UserActivity.GET_POST, UserActivity.ACTIVE_SESSION, UserActivity.DISPATCHED)
    machine.add_transition(UserActivity.SET_PRE_CHURN, UserActivity.ACTIVE_SESSION, UserActivity.PRE_CHURN)
    machine.add_transition(UserActivity.SET_PRE_CHURN, UserActivity.WAIT, UserActivity.PRE_CHURN)
    machine.add_transition(UserActivity.GET_POST, UserActivity.PRE_CHURN, UserActivity.DISPATCHED)
    machine.add_transition(UserActivity.OPEN_POST, UserActivity.DISPATCHED, UserActivity.OPENED)
    machine.add_transition(UserActivity.OPEN_POST, '*', UserActivity.OPENED)
    machine.add_transition(UserActivity.NO_OPEN, UserActivity.DISPATCHED, UserActivity.WAIT)
    machine.add_transition(UserActivity.GIVE_FEEDBACK, UserActivity.OPENED, UserActivity.FOLLOW_UP)
    machine.add_transition(UserActivity.GIVE_FEEDBACK, UserActivity.FOLLOW_UP, UserActivity.FOLLOW_UP)
    machine.add_transition(UserActivity.END_FEEDBACK, UserActivity.FOLLOW_UP, UserActivity.WAIT)
    machine.add_transition(UserActivity.NO_FEEDBACK, UserActivity.OPENED, UserActivity.WAIT)
