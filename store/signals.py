from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cart

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Create a cart automatically when a new user is created"""
    if created:
        Cart.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_cart(sender, instance, **kwargs):
    """Save the cart"""
    try:
        instance.cart.save()
    except Cart.DoesNotExist:
        Cart.objects.create(user=instance)
