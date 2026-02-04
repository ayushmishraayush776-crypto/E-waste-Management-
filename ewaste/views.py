from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import EWasteItem, EWasteCategory, PickupRequest, RecyclingFacility, Feedback, Notification, Company
from .forms import UserSignUpForm, EWasteItemForm, FeedbackForm, PickupRequestForm, UserEditForm


def home(request):
    """Home page"""
    total_items_collected = EWasteItem.objects.filter(is_collected=True).count()
    total_users = User.objects.count()
    total_categories = EWasteCategory.objects.count()
    
    context = {
        'total_items_collected': total_items_collected,
        'total_users': total_users,
        'total_categories': total_categories,
    }
    return render(request, 'home.html', context)


def about(request):
    """About page"""
    return render(request, 'about.html')


def how_it_works(request):
    """How it works page"""
    return render(request, 'how_it_works.html')


def facilities(request):
    """Recycling facilities page"""
    facilities = RecyclingFacility.objects.all()
    context = {'facilities': facilities}
    return render(request, 'facilities.html', context)


def contact(request):
    """Contact page with feedback form"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('home')
    else:
        form = FeedbackForm()
    
    context = {'form': form}
    return render(request, 'contact.html', context)


def signup(request):
    """User signup"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                # By default public signups are customers. Company membership must be granted via Django admin.

                messages.success(request, "Account created successfully! Please login.")
                return redirect('login')
    else:
        form = UserSignUpForm()
    
    context = {'form': form}
    return render(request, 'signup.html', context)


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_as = request.POST.get('login_as', 'customer')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # verify role matches selected login-as option
            login(request, user)
            # If user is staff, send to admin dashboard
            if user.is_staff:
                messages.success(request, f"Welcome back, {username}!")
                return redirect('admin_dashboard')

            # Ensure profile exists
            profile = getattr(user, 'profile', None)
            if login_as == 'company' and (not profile or not profile.is_company):
                logout(request)
                messages.error(request, "Your account is not a company member. Please choose the correct login type or sign up as a company member.")
                return redirect('login')
            if login_as == 'customer' and profile and profile.is_company:
                logout(request)
                messages.error(request, "Your account is a company member. Please choose 'Company Member' when logging in.")
                return redirect('login')

            messages.success(request, f"Welcome back, {username}!")
            if profile and profile.is_company:
                return redirect('company_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, 'registration/login.html')


@login_required(login_url='login')
def company_dashboard(request):
    """Company member dashboard: shows customer list and their submitted items"""
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    # allow filtering by customer
    selected_user = request.GET.get('user')

    customers = User.objects.filter(profile__is_company=False).annotate(items_count=Count('ewaste_items'))

    items = EWasteItem.objects.select_related('user', 'category')
    if selected_user:
        items = items.filter(user__id=selected_user)
    else:
        items = items.all()

    context = {
        'items': items,
        'customers': customers,
        'selected_user': int(selected_user) if selected_user else None,
    }
    return render(request, 'company_dashboard.html', context)


@login_required(login_url='login')
def user_list(request):
    """List users for company members to manage"""
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    users = User.objects.all()
    context = {'users': users}
    return render(request, 'users_list.html', context)


@login_required(login_url='login')
def edit_user(request, user_id):
    """Allow staff or company members to edit basic user settings"""
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect('user_list')
    else:
        form = UserEditForm(instance=target)

    context = {'form': form, 'target': target}
    return render(request, 'edit_user.html', context)


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    """User dashboard (redirect company members to company dashboard)"""
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_company:
        return redirect('company_dashboard')

    user_items = EWasteItem.objects.filter(user=request.user).prefetch_related('pickup_request')
    pending_pickups = PickupRequest.objects.filter(
        ewaste_item__user=request.user,
        status__in=['pending', 'scheduled']
    ).count()
    
    context = {
        'user_items': user_items,
        'pending_pickups': pending_pickups,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def report_ewaste(request):
    """Report e-waste item"""
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_company:
        messages.error(request, "Company members cannot report e-waste. Please use a customer account to report items.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EWasteItemForm(request.POST)
        if form.is_valid():
            ewaste_item = form.save(commit=False)
            ewaste_item.user = request.user
            ewaste_item.save()
            
            # Create pickup request
            PickupRequest.objects.create(ewaste_item=ewaste_item)
            
            messages.success(request, "E-waste item reported successfully! Pickup will be scheduled soon.")
            return redirect('dashboard')
    else:
        form = EWasteItemForm()
    
    context = {'form': form}
    return render(request, 'report_ewaste.html', context)


@login_required(login_url='login')
def my_items(request):
    """View user's reported items"""
    user_items = EWasteItem.objects.filter(user=request.user)
    context = {'user_items': user_items}
    return render(request, 'my_items.html', context)


@login_required(login_url='login')
def item_detail(request, item_id):
    """View item details"""
    item = get_object_or_404(EWasteItem, id=item_id)

    profile = getattr(request.user, 'profile', None)
    if item.user != request.user and not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to view this item!")
        return redirect('dashboard')

    pickup_request = PickupRequest.objects.filter(ewaste_item=item).first()

    context = {
        'item': item,
        'pickup_request': pickup_request,
    }
    return render(request, 'item_detail.html', context)


@login_required(login_url='login')
def manage_pickups(request):
    """Manage pickup requests (for admin/staff/company members)"""
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    pickups = PickupRequest.objects.all()

    if request.method == 'POST':
        pickup_id = request.POST.get('pickup_id')
        action = request.POST.get('action')
        pickup = get_object_or_404(PickupRequest, id=pickup_id)

        if action == 'accept':
            # Accept a pending pickup and assign to current user (mark scheduled)
            pickup.status = 'scheduled'
            pickup.assigned_to = request.user
            pickup.save()
            messages.success(request, "Pickup accepted and scheduled.")
        elif action == 'start':
            # Start the pickup - mark as in_progress and assign
            pickup.status = 'in_progress'
            pickup.assigned_to = request.user
            pickup.save()
            messages.success(request, "Pickup started (in progress).")
        elif action == 'schedule':
            pickup.status = 'scheduled'
            pickup.assigned_to = request.user
            pickup.save()
            messages.success(request, "Pickup scheduled successfully!")
        elif action == 'complete':
            pickup.status = 'completed'
            pickup.ewaste_item.is_collected = True
            pickup.save()
            pickup.ewaste_item.save()
            messages.success(request, "Pickup marked as completed!")
        elif action == 'cancel':
            pickup.status = 'cancelled'
            pickup.save()
            messages.success(request, "Pickup cancelled.")

    context = {'pickups': pickups}
    return render(request, 'manage_pickups.html', context)


@login_required(login_url='login')
def company_admin(request):
    """Company admin page (lists companies and recent pickups)"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    companies = Company.objects.all()
    recent_pickups = PickupRequest.objects.order_by('-created_at')[:10]

    context = {
        'companies': companies,
        'recent_pickups': recent_pickups,
    }
    return render(request, 'company_admin.html', context)


@login_required(login_url='login')
def edit_pickup(request, pickup_id):
    """Allow staff or company members to edit pickup details"""
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_staff and not (profile and profile.is_company):
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')

    pickup = get_object_or_404(PickupRequest, id=pickup_id)

    if request.method == 'POST':
        form = PickupRequestForm(request.POST, instance=pickup)
        if form.is_valid():
            pr = form.save(commit=False)
            # if not assigned, allow assigning to current user
            if not pr.assigned_to:
                pr.assigned_to = request.user
            pr.save()
            messages.success(request, "Pickup updated successfully!")
            return redirect('manage_pickups')
    else:
        form = PickupRequestForm(instance=pickup)

    context = {'form': form, 'pickup': pickup}
    return render(request, 'edit_pickup.html', context)


@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page!")
        return redirect('dashboard')
    
    total_items = EWasteItem.objects.count()
    collected_items = EWasteItem.objects.filter(is_collected=True).count()
    pending_pickups = PickupRequest.objects.filter(status='pending').count()
    total_users = User.objects.count()
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    companies_count = Company.objects.count()
    company_members = User.objects.filter(profile__is_company=True)
    
    context = {
        'total_items': total_items,
        'collected_items': collected_items,
        'pending_pickups': pending_pickups,
        'total_users': total_users,
        'notifications': notifications,
        'companies_count': companies_count,
        'company_members': company_members,
    }
    return render(request, 'admin_dashboard.html', context)


def search_items(request):
    """Search e-waste items"""
    query = request.GET.get('q', '')
    items = EWasteItem.objects.all()
    
    if query:
        items = items.filter(
            Q(item_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    context = {'items': items, 'query': query}
    return render(request, 'search_results.html', context)
