from django.db import models

# Create your models here.
class Driver(models.Model):
    uid = models.BigIntegerField(auto_created=True, primary_key=True)
    email = models.CharField(max_length=30, unique=True, null=False)
    name = models.CharField(max_length=10, null=False)
    password = models.CharField(max_length=20, default='123456')
    license = models.CharField(max_length=5, null=False)
    depotID = models.CharField(max_length=5, null=False)

    def __str__(self):
        return f"{self.uid}, {self.name}, {self.email}"
    
class Admin(models.Model):
    email = models.CharField(max_length=30, unique=True, null=False)
    name = models.CharField(max_length=10, null=False)
    password = models.CharField(max_length=20, default='admin123')
    uid = models.CharField(max_length=10, primary_key=True, null=False)
    depotID = models.CharField(max_length=5, null=False)

    def __str__(self):
        return f"{self.uid}, {self.name}, {self.email}"

