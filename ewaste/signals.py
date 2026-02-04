from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from django.contrib.auth.models import User
from .models import PickupRequest, Notification, Company


@receiver(post_save, sender=PickupRequest)
def pickup_request_created(sender, instance, created, **kwargs):
    """When a PickupRequest is created, notify staff users and company contacts."""
    if not created:
        return

    message = f"New pickup reported: {instance.ewaste_item.item_name} by {instance.ewaste_item.user.username}."
    url = reverse('manage_pickups')

    # Create in-app notifications for staff users
    staff_users = User.objects.filter(is_staff=True)
    for u in staff_users:
        Notification.objects.create(user=u, message=message, url=url)

    # Prepare email recipients (staff + company contacts)
    recipient_list = list(staff_users.values_list('email', flat=True))
    companies = Company.objects.all()
    recipient_list += [c.contact_email for c in companies if c.contact_email]
    recipient_list = [e for e in recipient_list if e]

    if recipient_list:
        subject = "New e-waste pickup reported"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
        except Exception:
            # Fail silently so app won't break if mail is not configured
            pass


# Auto-create a UserProfile whenever a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Import here to avoid circular import issues
        from .models import UserProfile
        UserProfile.objects.create(user=instance)
