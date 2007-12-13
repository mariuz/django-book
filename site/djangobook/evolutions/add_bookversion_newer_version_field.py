from django.db import models
from django_evolution.mutations import *

MUTATIONS = [
    AddField('BookVersion', 'newer_version', models.ForeignKey, null=True, related_model='djangobook.BookVersion')
]