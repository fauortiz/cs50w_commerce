from django.contrib import admin

from .models import *

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "datetime_created", "commenter", "listing")

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

class ListingInline(admin.StackedInline):
    model = Listing
    exclude = ('item','description','starting_bid','image_URL','seller','is_open','highest_bid')

class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        ListingInline,
    ]


admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)