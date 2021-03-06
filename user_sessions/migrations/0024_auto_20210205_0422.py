# Generated by Django 2.2.13 on 2021-02-05 04:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0023_auto_20210202_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='field_type',
            field=models.CharField(choices=[('text', 'Text'), ('quick_replies', 'Quick Replies'), ('buttons', 'Buttons'), ('save_values_block', 'Redirect Chatfuel block'), ('user_input', 'Save user input'), ('image', 'Send image'), ('condition', 'Condition'), ('set_attributes', 'Set Attributes'), ('redirect_session', 'Redirect session'), ('assign_sequence', 'Assign user to Sequence'), ('consume_service', 'Consume service')], max_length=50),
        ),
        migrations.CreateModel(
            name='AssignSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_id', models.IntegerField(default=0)),
                ('start_position', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('field', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_sessions.Field')),
            ],
        ),
    ]
