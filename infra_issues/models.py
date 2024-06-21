from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class InfraIssue(models.Model):
    id = models.AutoField(primary_key=True)
    complex_name = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
    issue = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    date = models.DateField()
    image = models.ImageField(
        upload_to='images/', null=True, blank=True)
    status = models.CharField(max_length=100, default='Pending')

    def __str__(self):
        return self.complex_name + " - " + self.room + " - " + self.issue + " - " + self.user + " - " + str(self.date) + " - " + self.status


class Profile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_number = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.user_id.username} - {self.email}"
