from django.db import models

# Create your models here.
class MLResult(models.Model):
    serialNumber = models.CharField(max_length=50)
    result = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'mlResult'