from django.db import models
from django_evolution.mutations import *

MUTATIONS = [
    AddField('Chapter', 'code', models.FileField, initial="", max_length=100, null=True)
]