from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_eventrequest_eventannouncement'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventrequest',
            name='request_type',
            field=models.CharField(
                choices=[('publish', 'Publish Request'), ('delete', 'Delete Request')],
                default='publish',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='eventrequest',
            name='delete_reason',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='President এর delete request এর কারণ',
            ),
        ),
    ]
