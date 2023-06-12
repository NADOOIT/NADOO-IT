from django.contrib import admin
from .models import Bot, BotPlatform, APIKey


class APIKeyInline(admin.TabularInline):
    model = APIKey
    readonly_fields = ("display_api_key",)
    extra = 1

    def display_api_key(self, obj):
        return obj.api_key

    display_api_key.short_description = "API Key"


class BotPlatformAdmin(admin.ModelAdmin):
    inlines = [APIKeyInline]
    list_display = ("id", "bot_name", "customer_name", "platform")
    list_filter = ("bot__name", "bot__customer__name", "platform")
    search_fields = ["bot__name", "bot__customer__name", "platform"]

    def bot_name(self, obj):
        return obj.bot.name

    bot_name.short_description = "Bot Name"

    def customer_name(self, obj):
        return obj.bot.customer.name

    customer_name.short_description = "Customer Name"


class BotPlatformInline(admin.StackedInline):
    model = BotPlatform
    extra = 1


class BotAdmin(admin.ModelAdmin):
    inlines = [BotPlatformInline]
    list_display = ("name", "customer")
    search_fields = ["name", "customer__name"]


admin.site.register(Bot, BotAdmin)
admin.site.register(BotPlatform, BotPlatformAdmin)
