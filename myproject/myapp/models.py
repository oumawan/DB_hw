from django.db import models

# Create your models here.
class User(models.Model):
    uid = models.BigIntegerField(primary_key=True, auto_created=True)
    email = models.CharField(max_length=39, unique=True)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    depotID = models.CharField(max_length=5, null=True)

    def __str__(self):
        return f"User {self.uid} - {self.email}"
    
class Admin(models.Model):
    uid = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin {self.uid}"
    
class Driver(models.Model):
    uid = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    license = models.CharField(max_length=5)

    def __str__(self):
        return f"Driver {self.uid}"
    
class Vehicle(models.Model):
    vid = models.BigIntegerField(primary_key=True, auto_created=True)
    lp = models.CharField(max_length=10)
    vtype = models.CharField(max_length=10)
    req = models.CharField(max_length=5)
    depotID = models.CharField(max_length=5)

    def __str__(self):
        return f"Vehicle {self.vid} - {self.lp}"

class Line(models.Model):
    lineNo = models.BigIntegerField(primary_key=True, auto_created=True)
    lineName = models.CharField(max_length=20)
    lineFrom = models.CharField(max_length=20)
    lineTo = models.CharField(max_length=20)
    depotID = models.CharField(max_length=5)
    vtype = models.CharField(max_length=5)

    def __str__(self):
        return f"Line {self.lineNo} - {self.lineName}"

class Schedule(models.Model):
    sid = models.BigIntegerField(primary_key=True, auto_created=True)
    dtime = models.DateTimeField()
    atime = models.DateTimeField()
    dlocation = models.CharField(max_length=20)
    lineNo = models.BigIntegerField(foreign_key=True)
    vid = models.BigIntegerField(foreign_key=True)
    uid = models.BigIntegerField(foreign_key=True)

    def __str__(self):
        return f"Schedule {self.sid} - Line {self.lineNo} - Vehicle {self.vid}"
    
class Leave(models.Model):
    uid = models.BigIntegerField(foreign_key=True)
    tbegin = models.DateTimeField()
    tend = models.DateTimeField()
    reason = models.CharField(max_length=100)

    def __str__(self):
        return f"Leave - User {self.uid} from {self.tbegin} to {self.tend}"
 
class Transfer(models.Model):
    vid = models.BigIntegerField(primary_key=True, auto_created=True)
    fromDepot = models.CharField(max_length=5)
    toDepot = models.CharField(max_length=5)
    date = models.DateTimeField()
    note = models.CharField(max_length=100)