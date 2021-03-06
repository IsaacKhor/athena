# Generated by Django 3.2 on 2021-05-31 23:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('title', models.CharField(blank=True, max_length=128, null=True)),
                ('desc', models.TextField(blank=True, verbose_name='description')),
                ('desc_format', models.IntegerField(choices=[(0, 'Plain Text'), (1, 'Markdown')], default=0, verbose_name='description format')),
                ('due_date', models.DateTimeField()),
                ('enforce_deadline', models.BooleanField(default=True)),
                ('max_grade', models.FloatField(default=100)),
                ('max_subs', models.IntegerField(blank=True, null=True, verbose_name='submission limit')),
                ('visible_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('autograde_mode', models.IntegerField(choices=[(0, 'No Autograder'), (1, 'Autograde - manually release results')], default=0, verbose_name='autograder options')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Submitted'), (1, 'Autograded'), (2, 'Instructor Graded'), (3, 'Past'), (4, 'Submitted')], default=0)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grader.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('term', models.IntegerField(choices=[(8, 'Fall'), (1, 'Spring'), (5, 'Summer')])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'unique_together': {('year', 'term')},
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.FloatField()),
                ('comments', models.TextField(blank=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('grader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='grader.submission')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('section', models.IntegerField()),
                ('title', models.CharField(max_length=128)),
                ('desc', models.TextField(blank=True)),
                ('desc_format', models.IntegerField(choices=[(0, 'Plain Text'), (1, 'Markdown')], default=0, verbose_name='description format')),
                ('instructors', models.ManyToManyField(related_name='instructors', to=settings.AUTH_USER_MODEL)),
                ('semester', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grader.semester')),
                ('students', models.ManyToManyField(blank=True, related_name='students', to=settings.AUTH_USER_MODEL)),
                ('tas', models.ManyToManyField(blank=True, related_name='tas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('semester', 'code', 'section')},
            },
        ),
        migrations.CreateModel(
            name='AutograderResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('result_dir', models.TextField()),
                ('score', models.FloatField(default=0)),
                ('visible', models.BooleanField(default=False)),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='grader.submission')),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grader.course'),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together={('code', 'course')},
        ),
    ]
