from django.db import models
from django.contrib.auth.models import User
import uuid


class Task(models.Model):
    """Example model for the blueprint"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title