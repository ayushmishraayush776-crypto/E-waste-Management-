from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('ewaste', 'UserProfile')

    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        ('ewaste', '0003_userprofile'),
    ]

    operations = [
        migrations.RunPython(create_profiles, reverse_code=migrations.RunPython.noop),
    ]
