from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from bot_management.plattforms.telegram.api import get_webhook_info, set_webhook
from .models import Bot, BotPlatform, APIKey, Message, Voice, VoiceFile


class APIKeyInline(admin.TabularInline):
    model = APIKey
    readonly_fields = ("display_api_key",)
    extra = 1

    def display_api_key(self, obj):
        return obj.api_key

    display_api_key.short_description = "API Key"


class BotPlatformAdmin(admin.ModelAdmin):
    inlines = [APIKeyInline]
    list_display = (
        "id",
        "bot_name",
        "customer_name",
        "platform",
        "webhook_status",
        "secret_url",
    )
    list_filter = ("bot__name", "bot__customer__name", "platform")
    search_fields = ["bot__name", "bot__customer__name", "platform"]

    def bot_name(self, obj):
        return obj.bot.name

    bot_name.short_description = "Bot Name"

    def customer_name(self, obj):
        return obj.bot.customer.name

    customer_name.short_description = "Customer Name"

    def webhook_status(self, obj):
        if obj.platform == "telegram":
            if obj.access_token:
                webhook_info = get_webhook_info(obj.access_token)
                if webhook_info and webhook_info.url:
                    return format_html('<span style="color: green;">Active</span>')
                else:
                    return format_html('<span style="color: red;">Inactive</span>')
            else:
                return "No access token"
        else:
            return "Not implemented"

    webhook_status.short_description = "Webhook Status"

    def activate_webhook(self, request, queryset):
        from django.contrib import messages

        for bot_platform in queryset:
            if bot_platform.platform == "telegram":
                base_url = settings.ALLOWED_HOSTS[0]
                webhook_url = f"https://{base_url}/bot/{bot_platform.platform}/webhook/{str(bot_platform.secret_url)}"
                if set_webhook(
                    bot_token=bot_platform.access_token,
                    webhook_url=webhook_url,
                    secret_token=str(bot_platform.secret_token)
                    # add other necessary parameters here
                ):
                    self.message_user(
                        request,
                        f"Webhook for {bot_platform.bot.name} has been activated successfully.",
                    )
                else:
                    messages.error(
                        request,
                        f"Failed to activate webhook for {bot_platform.bot.name}.",
                    )
            else:
                messages.warning(
                    request,
                    f"Activation of webhook for {bot_platform.bot.name} is not implemented for platform {bot_platform.platform}.",
                )

    activate_webhook.short_description = "Try to activate webhook"
    actions = [activate_webhook]


class BotPlatformInline(admin.StackedInline):
    model = BotPlatform
    extra = 1


class BotAdmin(admin.ModelAdmin):
    inlines = [BotPlatformInline]
    list_display = ("name", "customer")
    search_fields = ["name", "customer__name"]


admin.site.register(Voice)
admin.site.register(VoiceFile)
admin.site.register(Message)
admin.site.register(Bot, BotAdmin)
admin.site.register(BotPlatform, BotPlatformAdmin)
