import uuid
from django.db import models


class Company(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    logo = models.FileField(upload_to='company_logo/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name



