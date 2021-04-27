from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from posts.models import Author
@receiver(post_save, sender=User)
def user_as_author(sender,created,instance, **kwargs):
    if created:
        Author.objects.create(user=instance)
        
        print(instance)
        print(created)
        print(kwargs)
        print("author  biiug")

