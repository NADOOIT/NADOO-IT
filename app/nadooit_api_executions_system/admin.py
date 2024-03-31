# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the admin page for the nadooit_api_executions_system. Here you can register models that will then be shown on the admin page.
# Compatibility: Django 4
# License: TBD

from django.contrib import admin
from .models import CustomerProgramExecution

class CustomerProgramExecutionAdmin(admin.ModelAdmin):
    actions = ['delete_with_refund', 'delete_without_refund']

    def delete_with_refund(self, request, queryset):
        """
        Löscht die ausgewählten CustomerProgramExecution-Objekte und erstattet die Zeit dem zugehörigen Zeitkonto.
        """
        for obj in queryset:
            customer_program = obj.customer_program
            customer_program.time_account.time_balance_in_seconds += obj.program_time_saved_in_seconds
            customer_program.time_account.save()
            obj.delete()
    delete_with_refund.short_description = "Löschen mit Erstattung"

    def delete_without_refund(self, request, queryset):
        """
        Löscht die ausgewählten CustomerProgramExecution-Objekte ohne Erstattung der Zeit.
        """
        queryset.delete()
    delete_without_refund.short_description = "Löschen ohne Erstattung"

admin.site.register(CustomerProgramExecution, CustomerProgramExecutionAdmin)
