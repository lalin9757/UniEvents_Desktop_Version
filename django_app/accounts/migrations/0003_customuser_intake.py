from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='intake',
            field=models.CharField(blank=True, help_text='e.g. 49, 50, Fall-2022', max_length=20, null=True),
        ),
    ]
