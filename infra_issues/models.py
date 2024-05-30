from django.db import models

# Create your models here.


class InfraIssue(models.Model):
    complex_name = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
    issue = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    date = models.DateField()
    image = models.ImageField(
        upload_to='images/', null=True, blank=True)

    def __str__(self):
        return self.complex_name + " - " + self.room + " - " + self.issue + " - " + self.user + " - " + str(self.date)
