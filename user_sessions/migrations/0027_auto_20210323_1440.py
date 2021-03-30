# Generated by Django 3.1.4 on 2021-03-23 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0026_auto_20210223_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='field_type',
            field=models.CharField(choices=[('text', 'Text'), ('quick_replies', 'Quick Replies'), ('buttons', 'Buttons'), ('save_values_block', 'Redirect Chatfuel block'), ('user_input', 'Save user input'), ('image', 'Send image'), ('condition', 'Condition'), ('set_attributes', 'Set Attributes'), ('redirect_session', 'Redirect session'), ('assign_sequence', 'Subscribe user to Sequence'), ('unsubscribe_sequence', 'Unsubscribe user to Sequence'), ('one_time_notification', 'One Time Notification'), ('activate_ai', 'Activate AI'), ('deactivate_ai', 'Deactivate AI'), ('consume_service', 'Consume service')], max_length=50),
        ),
    ]