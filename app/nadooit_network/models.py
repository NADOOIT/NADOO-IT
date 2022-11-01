import uuid
from django.db import models
from nadooit_auth.models import User
from nadooit_program_ownership_system.models import ProgramShare

# Create your models here.


class NadooitInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Holds the amount of money in the inventory
    money = models.IntegerField(default=0)
    # Holds shares of programs
    list_of_nadooit_program_ownership_shares = models.ManyToManyField(
        ProgramShare, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)


class NadooitNetworkMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    inventory = models.ForeignKey(NadooitInventory, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.display_name + " " + self.user.user_code


class NadooitNetworkFriendslist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(NadooitNetworkMember, on_delete=models.CASCADE)
    friend_list = models.ManyToManyField(
        NadooitNetworkMember, related_name="friend_list"
    )

    def __str__(self):
        return (
            self.user.user.display_name
            + " "
            + self.user.user.user_code
            + " "
            + self.friend.user.user.display_name
            + " "
            + self.friend.user.user.user_code
        )


# Networt Groups are used to group users together for the purpose of working on a project together.
# A network group can be created by a user who is a member of the network.
#
class NadooitNetworkGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # the group is made up of members. There is a limit of 10 members in a group.
    members = models.ManyToManyField(NadooitNetworkMember, blank=True)
    created_by = models.ForeignKey(
        NadooitNetworkMember, on_delete=models.CASCADE, related_name="created_by"
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self) -> str:
        return (
            self.created_by.user.display_name
            + " "
            + self.created_by.user.user_code
            + " "
            + self.members.all().values_list("user.display_name", flat=True).join(", ")
        )


class NadooitNetworkGuildMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nadooit_network_member = models.ForeignKey(
        NadooitNetworkMember, on_delete=models.CASCADE
    )

    GUILD_ROLES = (
        ("MEMBER", "MEMBER"),
        ("MODERATOR", "MODERATOR"),
        ("ADMIN", "ADMIN"),
    )

    guild_role = models.CharField(choices=GUILD_ROLES, default="MEMBER", max_length=20)

    def __str__(self):
        return (
            self.nadooit_network_member.user.display_name
            + " "
            + self.guild_member.display_name
        )


class NadooitGuildBank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guild_inventory = models.ForeignKey(NadooitInventory, on_delete=models.CASCADE)

    # the amount of money the user has in the guild bank.


class NadooitGuild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    # Every guild has a members of type NadooitNetworkMember. Every NadooitNetworkMember can be a member of one guild.
    member_list = models.ManyToManyField(NadooitNetworkGuildMember, blank=True)
    guild_logo = models.ImageField(upload_to="guild_logo", blank=True, null=True)

    def __str__(self):
        return self.name
