# Generated by Django 5.1 on 2025-02-19 01:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_boy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.deliveryboy'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('accepted', 'Accepted'), ('delivered', 'Delivered')], max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='ProductImageFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('features', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myapp.product')),
            ],
        ),
    ]
