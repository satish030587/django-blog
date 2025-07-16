from django.contrib import admin
from .models import Post, Category, Tag, AuthorProfile, UserProfile

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'published', 'created_at']
    list_filter = ['category', 'published', 'created_at']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(AuthorProfile)
admin.site.register(UserProfile)




# Register your models here.
