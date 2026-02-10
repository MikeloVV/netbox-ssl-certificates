from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ssl_certificates', '0001_initial'),
    ]

    operations = [
        # Удалите старые индексы если они существуют
        migrations.RunSQL(
            sql="""
            DROP INDEX IF EXISTS netbox_ssl_name_idx;
            DROP INDEX IF EXISTS netbox_ssl_cn_idx;
            DROP INDEX IF EXISTS netbox_ssl_valid_until_idx;
            DROP INDEX IF EXISTS netbox_ssl_expired_idx;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Создайте новые индексы с правильными именами
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['name'], name='netbox_ssl_cert_name_idx'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['common_name'], name='netbox_ssl_cert_cn_idx'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['valid_until'], name='netbox_ssl_cert_valid_idx'),
        ),
        migrations.AddIndex(
            model_name='certificate',
            index=models.Index(fields=['is_expired'], name='netbox_ssl_cert_expired_idx'),
        ),
    ]