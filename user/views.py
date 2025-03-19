import json
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from jinja2 import Environment, FileSystemLoader
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.contrib.auth.hashers import make_password
from user.models import ChatGroup, GroupMessage, Login, Register
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .forms import  ChatmessageCreateForm
from django.db.models import Prefetch
from django.core.exceptions import PermissionDenied
from django.conf import settings
import pusher
# Create your views here.

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

#Email Configrations
def generate_otp():
    return str(random.randint(100000, 999999))


def send_test_email(email, otp , first_name):
    
    sender_email = "monty131419@gmail.com"
    app_password = "anicozktxbfdnmzj" 
    receiver_email = email
    subject = "OTP Verification 🚀"

    env = Environment(loader=FileSystemLoader('email_template'))  
    template = env.get_template('otp.html')  
    html_content = template.render(otp=otp,first_name =first_name)  # Bind dynamic data

    # Create the email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Attach the rendered HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return True  

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False  
    
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the email already exists in the Register model
        if Register.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists!')
            return HttpResponseRedirect(request.path_info)

        hashed_password = make_password(password)
        
        otp = generate_otp()
        
        email_sent = send_test_email(email, otp,first_name)

        if not email_sent:
            return render(request, "register_user.html", {"error": "Error sending OTP email."})

        # Save the data into the Register model
        register_obj = Register(
            First_name=first_name,
            Last_name=last_name,
            email=email,
            password=hashed_password,
            otp=otp # Consider hashing the password
        )
        register_obj.save()
        
        chat_group_name = f"{first_name}"  # Unique name for each user
        chat_group, created = ChatGroup.objects.get_or_create(group_name=chat_group_name)

        if created:
            chat_group.members.add(register_obj)

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')  # Redirect to the login page

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        otp = request.POST.get('otp', '').strip()

        print(f"Login attempt: Email={email}, OTP={otp}")

        if not email or not otp:
            return render(request, 'login.html', {'alert': 'Email and OTP are required.'})

        try:
            user = Register.objects.get(email=email)
            print(f"User found: {user}")
        except Register.DoesNotExist:
            messages.warning(request, 'Email not matched!')
            return render(request, 'login.html')

        if not check_password(password, user.password):
            messages.warning(request, 'Password is incorrect!')
            return render(request, 'login.html')

        if user.otp != otp:
            messages.warning(request, 'OTP not matched!')
            return render(request, 'login.html')

        # Store login details in Login model
        login_entry = Login.objects.create(
            user_id=user,
            email=user.email,
            password=user.password,  # You may store hashed password if required
            otp=otp
        )

        # Manually set session data
        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
        request.session['user_first_name'] = user.First_name
        request.session['is_authenticated'] = True

        print(f"Session data set: {request.session.items()}")

        messages.success(request, 'Logged in successfully!')
        return redirect('home')

    return render(request, 'login.html')

def logout_user(request):
    request.session.flush()  # Clear all session data
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

#Forgot Password Implementations
def send_test_email_forgot(email, otp , first_name):
    
    sender_email = "monty131419@gmail.com"
    app_password = "anicozktxbfdnmzj" 
    receiver_email = email
    subject = "Reset Password OTP Verification 🚀"

    env = Environment(loader=FileSystemLoader('email_template'))  
    template = env.get_template('forgot_otp.html')  
    html_content = template.render(otp=otp,first_name =first_name)  # Bind dynamic data

    # Create the email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Attach the rendered HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return True  

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Register.objects.get(email=email)
            otp = generate_otp()
            user.otp = otp
            user.save()

            email_sent = send_test_email_forgot(email, otp, user.First_name)
            if email_sent:
                messages.success(request, 'OTP sent to your email.')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')

        except Register.DoesNotExist:
            messages.error(request, 'Email not registered.')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            user = Register.objects.get(email=email, otp=otp)
            messages.success(request, 'OTP verified. Please set a new password.')
            return redirect('reset_password')
        except Register.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('password')

        try:
            user = Register.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            messages.success(request, 'Password reset successfully. Please log in.')
            return redirect('login')

        except Register.DoesNotExist:
            messages.error(request, 'Failed to reset password. Please try again.')
            return redirect('reset_password')

    return render(request, 'reset_password.html')

def create_group(request):
    print("Create Group View Called")
    
    # Debug: Print session data
    print("Session data:", request.session.items())
    
    # Check if the user is authenticated
    if not request.session.get('is_authenticated'):
        print("User not authenticated. Redirecting to login.")
        return redirect('login')  # Redirect to login if the user is not authenticated

    if request.method == "POST":
        group_name = request.POST.get("group_name")
        members = request.POST.getlist("members")  # Get the list of member IDs
        avatar = request.FILES.get("avatar")

        print("Group Name Submitted:", group_name)
        print("Avatar Submitted:", avatar)
        print("Members Submitted:", members)

        if group_name:
            # Ensure all member IDs are valid integers
            try:
                members = [int(member_id) for member_id in members]  # Convert IDs to integers
                user_instances = Register.objects.filter(id__in=members)
            except ValueError:
                return render(request, 'create_group.html', {'error': 'Invalid member ID(s)'})

            new_group, created = ChatGroup.objects.get_or_create(group_name=group_name)
            if created:
                if avatar:
                    new_group.avatar = avatar  # Store the avatar URL in the database
                # Add members to the group (many-to-many relationship)
                new_group.members.set(user_instances)  # Associate members with the group
                new_group.save()
                
                messages.success(request, f'🎉 Group "{group_name}" created successfully!')

                print("Group Created:", new_group.group_name)
                return redirect('chat_view', group_name=group_name)
            else:
                print("Group already exists.")
                return render(request, 'chat_view.html', {'error': 'Group already exists'})
        else:
            print("Invalid Group Name")
            return render(request, 'chat_view.html', {'error': 'Invalid group name'})

    # Fetch only the logged-in user for the members list
    users = Register.objects.exclude(id=request.session.get('user_id'))  # Exclude the logged-in user from being added to the group

    return render(request, 'chat_view.html', {'users': users})


def chat_view(request, group_name=None):
    # Fetch logged-in user details
    user_id = request.session.get('user_id')
    if not user_id:
        raise PermissionDenied("User not authenticated.")
    
    try:
        logged_in_user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        request.session.flush()  # Clear invalid session
        raise PermissionDenied("Invalid user session.")

    print("Logged-in user:", logged_in_user.email)

    # Fetch all chat groups and related messages
    chat_groups = ChatGroup.objects.prefetch_related(
        Prefetch(
            'chat_messages',
            queryset=GroupMessage.objects.order_by('-created'),
            to_attr='latest_messages'
        )
    ).all()

    if not group_name:
        return render(request, 'chat_view.html', {
            'user': logged_in_user,
            'group_name': None,
            'chat_messages': None,
            'chat_groups': chat_groups,
        })

    # Fetch specific group and its messages
    chat_group = get_object_or_404(ChatGroup, group_name=group_name)
    chat_messages = chat_group.chat_messages.all() 
    

    # Get the latest message in the group
    last_message = chat_group.chat_messages.first()

    if logged_in_user not in chat_group.members.all():
        chat_group.members.add(logged_in_user)
        # messages.success(request, f'🎉 {logged_in_user.First_name} joined the group "{group_name}"!')
        
    pusher_client.trigger(
            f'chat-group-{group_name}',  # Channel name
            'user-joined',  # Event name
            {
                'message': f'🚀 {logged_in_user.First_name} joined "{group_name}"!',
                'user': logged_in_user.First_name
            }
        )
        
    form = ChatmessageCreateForm() 

    if request.method == 'POST':
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = logged_in_user
            message.group = chat_group
            message.save()
            return redirect('chat_view', group_name=group_name)

    return render(request, 'chat_view.html', {
        'user': logged_in_user,
        'group_name': chat_group.group_name,
        'chat_messages': chat_messages,
        'last_message': last_message,
        'form': form,
        'chat_groups': chat_groups,
    })
    

def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        file_type = file.content_type  # Get the MIME type of the file
        file_name = file.name

        # Save the file to the chat_attachments folder
        upload_path = os.path.join(settings.MEDIA_ROOT, "chat_attachments", file_name)
        with open(upload_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Return the relative file path and type
        file_path = os.path.join("chat_attachments", file_name)
        return JsonResponse({
            "file_url": file_path,  # Return relative path
            "file_type": file_type,
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

