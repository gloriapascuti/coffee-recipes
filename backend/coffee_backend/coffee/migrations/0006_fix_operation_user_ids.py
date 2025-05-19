from django.db import migrations

def fix_operation_user_ids(apps, schema_editor):
    Operation = apps.get_model('coffee', 'Operation')
    User = apps.get_model('auth', 'User')
    for op in Operation.objects.all():
        username = op.user.username
        try:
            correct_user = User.objects.get(username=username)
            if op.user_id != correct_user.id:
                op.user_id = correct_user.id
                op.save(update_fields=['user_id'])
        except User.DoesNotExist:
            print(f"User not found for operation id={op.id}, username={username}")

class Migration(migrations.Migration):
    dependencies = [
        ('coffee', '0005_alter_operation_user'),
    ]
    operations = [
        migrations.RunPython(fix_operation_user_ids),
    ] 