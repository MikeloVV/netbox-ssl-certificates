from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ssl_certificates', '0002_update_indexes'),
        ('dcim', '0001_initial'),
        ('virtualization', '0001_initial'),
    ]

    operations = [
        # Add device relations
        migrations.AddField(
            model_name='certificate',
            name='devices',
            field=models.ManyToManyField(
                blank=True,
                help_text='Devices using this certificate',
                related_name='certificates',
                to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='certificate',
            name='virtual_machines',
            field=models.ManyToManyField(
                blank=True,
                help_text='Virtual machines using this certificate',
                related_name='certificates',
                to='virtualization.virtualmachine'
            ),
        ),
        migrations.AddField(
            model_name='certificate',
            name='sites',
            field=models.ManyToManyField(
                blank=True,
                help_text='Sites using this certificate',
                related_name='certificates',
                to='dcim.site'
            ),
        ),
        # Add CA certificate field
        migrations.AddField(
            model_name='certificate',
            name='ca_certificate',
            field=models.ForeignKey(
                blank=True,
                help_text='CA certificate for chain verification',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='signed_certificates',
                to='netbox_ssl_certificates.certificate'
            ),
        ),
        # Add chain verification fields
        migrations.AddField(
            model_name='certificate',
            name='chain_verified',
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text='Certificate chain verification status'
            ),
        ),
        migrations.AddField(
            model_name='certificate',
            name='chain_verification_message',
            field=models.TextField(
                blank=True,
                editable=False,
                help_text='Chain verification details'
            ),
        ),
    ]