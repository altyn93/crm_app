from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_order_completed_at_employee_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessprofile',
            name='max_employees',
            field=models.PositiveIntegerField(default=20, verbose_name='Максимум сотрудников'),
        ),
    ]
