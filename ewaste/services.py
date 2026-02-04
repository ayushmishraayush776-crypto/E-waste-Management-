from django.db.models import Count, Q
from django.utils import timezone
from .models import EWasteItem, PickupRequest, RecyclingFacility


def get_user_statistics(user):
    """
    Get statistics for a specific user
    """
    total_items = EWasteItem.objects.filter(user=user).count()
    collected_items = EWasteItem.objects.filter(user=user, is_collected=True).count()
    pending_items = EWasteItem.objects.filter(user=user, is_collected=False).count()
    
    return {
        'total_items': total_items,
        'collected_items': collected_items,
        'pending_items': pending_items,
    }


def get_global_statistics():
    """
    Get global platform statistics
    """
    total_items = EWasteItem.objects.count()
    collected_items = EWasteItem.objects.filter(is_collected=True).count()
    pending_pickups = PickupRequest.objects.filter(status__in=['pending', 'scheduled']).count()
    completed_pickups = PickupRequest.objects.filter(status='completed').count()
    
    return {
        'total_items': total_items,
        'collected_items': collected_items,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
    }


def get_category_statistics():
    """
    Get statistics by category
    """
    categories = EWasteItem.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return list(categories)


def get_pending_pickups():
    """
    Get all pending pickup requests
    """
    return PickupRequest.objects.filter(
        status__in=['pending', 'scheduled']
    ).select_related('ewaste_item', 'assigned_to').order_by('-created_at')


def schedule_pickup(pickup_request, scheduled_date, assigned_staff):
    """
    Schedule a pickup request
    """
    pickup_request.status = 'scheduled'
    pickup_request.scheduled_date = scheduled_date
    pickup_request.assigned_to = assigned_staff
    pickup_request.save()
    return pickup_request


def complete_pickup(pickup_request):
    """
    Mark a pickup as completed
    """
    pickup_request.status = 'completed'
    pickup_request.completed_date = timezone.now()
    pickup_request.ewaste_item.is_collected = True
    pickup_request.save()
    pickup_request.ewaste_item.save()
    return pickup_request


def find_nearby_facilities(latitude, longitude, radius_km=10):
    """
    Find recycling facilities within a radius
    (Note: Requires latitude/longitude in RecyclingFacility model)
    """
    facilities = RecyclingFacility.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).all()
    
    return facilities


def get_facility_capacity():
    """
    Get current capacity of facilities
    """
    facilities = RecyclingFacility.objects.annotate(
        pending_items=Count('ewaste_item', filter=Q(ewaste_item__is_collected=False))
    )
    
    return facilities


def export_user_items_data(user):
    """
    Export user's items data for backup/report
    """
    items = EWasteItem.objects.filter(user=user).values(
        'id', 'item_name', 'category__name', 'condition', 'quantity',
        'is_collected', 'created_at'
    )
    
    return list(items)
