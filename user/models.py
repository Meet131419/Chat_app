from django.db import models
from django.utils.timezone import now
from django.utils.timezone import localtime
from django.conf import settings
# Create your models here.

class Login(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Register',on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100,default=1)
    otp = models.CharField(max_length=6,default='123456') 
    
    def __str__(self):
        return f"{self.user_id}"
    
class Register(models.Model):
    id = models.AutoField(primary_key=True)
    First_name = models.CharField(max_length=50)
    Last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, blank=True, null=True)
    date_joined = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"#{self.id} - {self.First_name}"
    
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(Register)
    avatar = models.ImageField(upload_to='chat_group_avatars/', blank=True, null=True)
    
    def __str__(self):
        return self.group_name
    
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(Register, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


    @property
    def file_url(self):
        if self.file:
            return f"{settings.MEDIA_URL}{self.file}"
        return None
    
    @property
    def is_image(self):
        return self.file_type.startswith('image') if self.file_type else False

    @property
    def is_video(self):
        return self.file_type.startswith('video') if self.file_type else False
    
    @property
    def is_pdf(self):
        return self.file_type.startswith('application/pdf') if self.file_type else False
    
    @property
    def is_audio(self):
        return self.file_type.startswith('audio') if self.file_type else False

    def formatted_time(self):
        return localtime(self.created).strftime('%I:%M %p')

    def author_name(self):
        return self.author.First_name

    def __str__(self):
        return f'{self.author.First_name} : {self.body or "File Attachment"}'

    class Meta:
        ordering = ['-created']
        
