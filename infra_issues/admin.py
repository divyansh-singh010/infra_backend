from django.contrib import admin
from infra_issues.models import InfraIssue

# Register your models here.

class InfraIssueAdmin(admin.ModelAdmin):
    list_display = ('complex_name', 'room', 'issue', 'user', 'date')
    search_fields = ('complex_name', 'room', 'issue', 'user', 'date')
    list_filter = ('complex_name', 'room', 'issue', 'user', 'date')


admin.site.register(InfraIssue, InfraIssueAdmin)