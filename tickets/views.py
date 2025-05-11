import uuid
import json
import requests
from django.utils import timezone
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Plan, AccessTicket
 # You'll define this below



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import AccessTicket


def dashboard(request):
    user = request.user
    tickets = AccessTicket.objects.filter(user=user).order_by('-created_at')
    profile = user.userprofile  # Assumes you’ve linked UserProfile with OneToOneField

    context = {
        'user': user,
        'profile': profile,
        'tickets': tickets,
    }
    return render(request, 'tickets/dashboard.html', context)


from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
#this part is to regster
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('custom_login')
    else:
        form = SignUpForm()
    return render(request, 'tickets/signup.html', {'form': form})





def update_profile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Or wherever you want to go after update
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'tickets/user_profile.html', {'form': form})


# Step 1: Customer chooses a plan and pays
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import uuid
import requests
from .models import AccessTicket, Plan
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import uuid
import requests
import json
from .models import AccessTicket, Plan

@login_required
def create_ticket(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        duration_months = int(request.POST.get('duration', 1))
        phone_number = request.POST.get('phone_number')

        if not plan_id or not phone_number:
            return render(request, 'tickets/error.html', {'message': 'Please select a plan and enter your phone number.'})

        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return render(request, 'tickets/error.html', {'message': 'Invalid plan selected.'})

        ticket_code = f"{request.user.username}-{uuid.uuid4().hex[:8]}"

        ticket = AccessTicket.objects.create(
            user=request.user,
            ticket_code=ticket_code,
            plan_name=plan.name,
            data_limit_mb=1000,
            expiry_date=timezone.now() + timezone.timedelta(weeks=4 * duration_months),
            is_active=False,
        )

        # === Initiate payment ===
        api_url = "https://api-checkout.cinetpay.com/v2/payment"
        headers = {'Content-Type': 'application/json'}
        payload = {
    "apikey": settings.CINETPAY_API_KEY,
    "site_id": settings.CINETPAY_SITE_ID,
    "transaction_id": ticket_code,
    "amount": int(plan.price),  # Ensure this is an integer
    "currency": "GNF",
    "description": f"Payment for plan {plan.name}",
    "customer_name": request.user.username,
    "customer_surname": "N/A",
    "customer_email": request.user.email,
    "customer_phone_number": phone_number,   # 🔧 <- Set YOUR number here
    "notify_url": request.build_absolute_uri('/payment-notify/'),
    "return_url": request.build_absolute_uri('/payment-return/'),
    "cancel_url": request.build_absolute_uri('/payment-cancel/'),
    "channels": "MOBILE_MONEY"  # 🔧 <- Use valid value (ALL, MOBILE_MONEY, WALLET, CREDIT_CARD)
}


        try:
            print("CinetPay payload:", json.dumps(payload, indent=2))  # Debug: Log request payload

            response = requests.post(api_url, headers=headers, json=payload)
            res_data = response.json()
            print("CinetPay response:", json.dumps(res_data, indent=2))  # Debug: Log response

            if res_data.get("code") == "201":
                return redirect(res_data['data']['payment_url'])
            else:
                return render(request, 'tickets/error.html', {
                    'message': f"Payment failed: {res_data.get('message', 'Unknown error.')}"
                })
        except ValueError:
            return render(request, 'tickets/error.html', {'message': 'Invalid response from payment gateway.'})
        except Exception as e:
            return render(request, 'tickets/error.html', {'message': f"Payment request error: {e}"})

    else:
        plans = Plan.objects.all()
        return render(request, 'tickets/create_tickets.html', {'plans': plans})





from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import json

from .models import AccessTicket, MikroTikRouter
from .mikrotik_api import connect_router
from .sms_notification import send_sms  # Make sure this is created

from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import json
from .models import AccessTicket, MikroTikRouter
from .mikrotik_api import connect_router
from .sms_notification import send_sms  # Ensure this is created

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import AccessTicket, MikroTikRouter
from .mikrotik_api import connect_router
from .sms_notification import send_sms  # Ensure this function is implemented


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import AccessTicket, MikroTikRouter
from .mikrotik_api import connect_router
 # Your custom SMS function

@csrf_exempt
def payment_notify(request):
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')

        if not transaction_id or not status:
            return JsonResponse({'message': 'Missing required fields.'}, status=400)

        if status != 'ACCEPTED':
            return JsonResponse({'message': 'Payment not accepted.'}, status=200)

        try:
            ticket = AccessTicket.objects.get(ticket_code=transaction_id)
        except AccessTicket.DoesNotExist:
            return JsonResponse({'message': 'Ticket not found.'}, status=404)

        if ticket.is_active:
            return JsonResponse({'message': 'Ticket already active.'}, status=200)

        # Activate the ticket
        ticket.is_active = True
        password = ticket.generate_random_password()
        ticket.router_password = password
        ticket.save()

        # Connect to MikroTik router
        router = MikroTikRouter.objects.first()
        if router:
            api = connect_router(router.ip_address, router.username, router.password, router.api_port)
            if api:
                # Check if Hotspot user already exists
                user_exists = list(api(cmd='/ip/hotspot/user/print', **{"?name": ticket.ticket_code}))
                if not user_exists:
                    api(cmd='/ip/hotspot/user/add', **{
                        "name": ticket.ticket_code,
                        "password": password,
                        "profile": ticket.plan_name
                    })
                    print(f"[MikroTik] Hotspot user {ticket.ticket_code} created.")
                else:
                    print(f"[MikroTik] User {ticket.ticket_code} already exists.")
            else:
                print("[MikroTik] Connection failed.")
        else:
            print("[MikroTik] No router configured.")

        # Send email
        send_mail(
            subject="Your Internet Access Ticket",
            message=(
                f"Hello {ticket.user.username},\n\n"
                f"Your internet access is now active.\n\n"
                f"Username: {ticket.ticket_code}\n"
                f"Password: {password}\n"
                f"Plan: {ticket.plan_name}\n"
                f"Expires: {ticket.expiry_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                "Thank you!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.user.email],
            fail_silently=True
        )

        # Send SMS
        profile = getattr(ticket.user, 'profile', None)
        if profile and profile.phone_number:
            sms_message = (
                f"✅ Wi-Fi Access Active!\n"
                f"User: {ticket.ticket_code}\n"
                f"Pass: {password}\n"
                f"Plan: {ticket.plan_name}\n"
                f"Expires: {ticket.expiry_date.strftime('%Y-%m-%d %H:%M')}"
            )
            send_sms(profile.phone_number, sms_message)
        else:
            print("[SMS] No phone number available in user profile.")

        return JsonResponse({'message': 'Payment processed and ticket activated successfully.'})

    except Exception as e:
        print("Notify Error:", e)
        return JsonResponse({'message': 'Internal server error.'}, status=500)

def payment_return(request):
    return render(request, 'tickets/payment_success.html')  # Create this template

def payment_cancel(request):
    return render(request, 'tickets/payment_cancel.html')  # Create this template


import requests
from django.conf import settings

def send_sms(to_number, message):
    api_url = "https://client.cinetpay.com/sms/send"
    payload = {
        "apikey": settings.CINETPAY_API_KEY,
        "from": "YourName",  # Your registered sender name
        "to": to_number,
        "text": message,
        "content_type": 1  # Optional: set to 1 for plain text
    }

    try:
        response = requests.post(api_url, data=payload)
        result = response.json()
        print("[SMS] CinetPay response:", result)
        return result
    except Exception as e:
        print("[SMS] Failed to send:", e)
        return None




from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # or any page after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'tickets/login.html', {'form': form})
