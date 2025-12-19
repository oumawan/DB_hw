from django.db import models

# Create your models here.
class User(models.Model):
    uid = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    depotID = models.CharField(max_length=5)

    def __str__(self):
        return f"User {self.uid} - {self.email}"
    
class Admin(models.Model):
    uid = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin {self.uid}"
    
class Driver(models.Model):
    uid = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='driver_profile')
    license = models.CharField(max_length=5)

    def __str__(self):
        return f"Driver {self.uid}"
    
class Vehicle(models.Model):
    vid = models.BigAutoField(primary_key=True)
    lp = models.CharField(max_length=10)
    vtype = models.CharField(max_length=10)
    depotID = models.CharField(max_length=5)

    def __str__(self):
        return f"Vehicle {self.vid} - {self.lp}"

class Line(models.Model):
    lineNo = models.BigAutoField(primary_key=True)
    lineName = models.CharField(max_length=20)
    lineFrom = models.CharField(max_length=20)
    lineTo = models.CharField(max_length=20)
    depotID = models.CharField(max_length=5)
    vtype = models.CharField(max_length=10)
    run_duration = models.BigIntegerField()

    def __str__(self):
        return f"Line {self.lineNo} - {self.lineName}"

class Schedule(models.Model):
    sid = models.BigAutoField(primary_key=True)
    dtime = models.DateTimeField()
    atime = models.DateTimeField()
    dlocation = models.CharField(max_length=20)
    lineNo = models.ForeignKey(Line, on_delete=models.PROTECT, related_name='schedules')
    vid = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='schedules')
    uid = models.ForeignKey(User, on_delete=models.PROTECT, related_name='schedules')

    def __str__(self):
        return f"Schedule {self.sid} - Line {self.lineNo} - Vehicle {self.vid}"
    
class Leave(models.Model):
    lid = models.BigAutoField(primary_key=True)
    approved = models.CharField(max_length=1) # 'Y' or 'N'
    uid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    tbegin = models.DateTimeField()
    tend = models.DateTimeField()
    reason = models.CharField(max_length=100)

    def __str__(self):
        return f"Leave - User {self.uid} from {self.tbegin} to {self.tend}"

class Transfer(models.Model):
    vid = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='transfers')
    fromDepot = models.CharField(max_length=5)
    toDepot = models.CharField(max_length=5)
    date = models.DateField()
    note = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"Transfer - Vehicle {self.vid} from {self.fromDepot} to {self.toDepot} on {self.data}"