# Generated by Django 4.1.5 on 2023-05-27 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0003_rename_created_date_user_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singer',
            name='cover_path',
            field=models.CharField(default='https://hypermusic-1317300880.cos.ap-beijing.myqcloud.com/Default_Singer_Avator.png', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar_path',
            field=models.CharField(default='https://hypermusic-1317300880.cos.ap-beijing.myqcloud.com/Default_User_Avator.png', max_length=100),
        ),
    ]
