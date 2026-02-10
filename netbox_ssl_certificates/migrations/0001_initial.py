from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False
                )),
                ('created', models.DateTimeField(
                    auto_now_add=True,
                    null=True
                )),
                ('last_updated', models.DateTimeField(
                    auto_now=True,
                    null=True
                )),
                ('custom_field_data', models.JSONField(
                    blank=True,
                    default=dict,
                    encoder=utilities.json.CustomFieldJSONEncoder
                )),
                ('name', models.CharField(
                    max_length=200,
                    unique=True,
                    help_text='Unique name for the certificate'
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text='Description of the certificate'
                )),
                ('certificate_file', models.TextField(
                    help_text='PEM encoded certificate content'
                )),
                ('private_key', models.TextField(
                    blank=True,
                    help_text='PEM encoded private key (optional)'
                )),
                ('common_name', models.CharField(
                    max_length=255,
                    blank=True,
                    editable=False
                )),
                ('subject_alternative_names', models.JSONField(
                    default=list,
                    blank=True,
                    help_text='List of SANs'
                )),
                ('issuer', models.CharField(
                    max_length=255,
                    blank=True,
                    editable=False
                )),
                ('serial_number', models.CharField(
                    max_length=100,
                    blank=True,
                    editable=False
                )),
                ('valid_from', models.DateTimeField(
                    null=True,
                    blank=True,
                    editable=False
                )),
                ('valid_until', models.DateTimeField(
                    null=True,
                    blank=True,
                    editable=False
                )),
                ('fingerprint_sha256', models.CharField(
                    max_length=95,
                    blank=True,
                    editable=False,
                    help_text='SHA-256 fingerprint'
                )),
                ('is_self_signed', models.BooleanField(
                    default=False,
                    editable=False
                )),
                ('key_size', models.IntegerField(
                    null=True,
                    blank=True,
                    editable=False
                )),
                ('algorithm', models.CharField(
                    max_length=50,
                    blank=True,
                    editable=False
                )),
                ('is_expired', models.BooleanField(
                    default=False,
                    editable=False
                )),
                ('days_until_expiry', models.IntegerField(
                    null=True,
                    blank=True,
                    editable=False
                )),
                ('comments', models.TextField(
                    blank=True
                )),
                ('tags', taggit.managers.TaggableManager(
                    through='extras.TaggedItem',
                    to='extras.Tag',
                    blank=True
                )),
            ],
            options={
                'verbose_name': 'SSL Certificate',
                'verbose_name_plural': 'SSL Certificates',
                'ordering': ['name'],
            },
        ),
    ]