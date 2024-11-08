from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid
import os

def validate_file_type(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf']
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file type. Only PDF files are allowed.')
    
def validate_audio_type(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp3', 'ogg', 'webm', 'wav']
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file type. Only Audio files are allowed.')

class Law(models.Model):
    name = models.CharField(max_length=555, blank=False, null=False)
    name_bn = models.CharField(max_length=555, blank=False, null=False)
    file = models.FileField(upload_to='laws/', validators=[validate_file_type], blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if Law.objects.exists() and not self.pk:
            raise ValidationError('There can be only one Law instance.')
        
        try:
            this = Law.objects.get(pk=self.pk)
            if this.file != self.file:
                this.file.delete(save=False)
        except Law.DoesNotExist:
            pass

        super(Law, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super(Law, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Radio(models.Model):
    name = models.CharField(max_length=555, blank=False, null=False)
    name_bn = models.CharField(max_length=555, blank=False, null=False)
    file = models.FileField(upload_to='radios/', validators=[validate_audio_type], blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if Radio.objects.exists() and not self.pk:
            raise ValidationError('There can be only one Radio instance.')
        
        try:
            this = Radio.objects.get(pk=self.pk)
            if this.file != self.file:
                this.file.delete(save=False)
        except Radio.DoesNotExist:
            pass

        super(Radio, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super(Radio, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=1000, blank=False, null=False)
    name_bn = models.CharField(max_length=1000, blank=False, null=False)
    sequence = models.PositiveIntegerField(unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_sequence = Service.objects.aggregate(models.Max('sequence'))['sequence__max']
            if last_sequence is None:
                self.sequence = 1
            else:
                self.sequence = last_sequence + 1
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.sequence}: {self.name}'

@receiver(post_delete, sender=Service)
def reorder_sequence(sender, instance, **kwargs):
    services = Service.objects.order_by('sequence')
    for idx, service in enumerate(services, start=1):
        if service.sequence != idx:
            service.sequence = idx
            service.save()

class District(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_bn = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Thana(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_bn = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
class PrimaryThana(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_bn = models.CharField(max_length=255, blank=False, null=False)
    thanas = models.ManyToManyField('Thana', related_name='primary_thanas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Contact(models.Model):
    designation = models.CharField(max_length=255, blank=False, null=False)
    designation_bn = models.CharField(max_length=255, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    thana = models.ForeignKey('PrimaryThana', related_name='contact', on_delete=models.CASCADE, null=False, blank=False,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.designation + ' - ' + self.thana.name

class Region(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_bn = models.CharField(max_length=255, blank=False, null=False)
    districts = models.ManyToManyField('District', related_name='regions')
    thanas = models.ManyToManyField('PrimaryThana', related_name='regions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class HelpDesk(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    name_bn = models.CharField(max_length=255, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# TICKET_STATUS_CHOICES = [
#     ('awaiting', 'Awaiting'),
#     ('answered', 'Answered'),
#     ('closed', 'Closed'),
# ]

# # Model for the Ticket
# class Ticket(models.Model):
#     ticket_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     subject = models.CharField(max_length=500, blank=False, null=False)
#     address = models.CharField(max_length=800, blank=True, null=True)
#     phone_number = models.CharField(max_length=15, blank=False, null=False)
#     email = models.EmailField(blank=True, null=True)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
#     status = models.CharField(max_length=10, choices=TICKET_STATUS_CHOICES, default='awaiting')  # Ticket status
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f'Ticket #{self.ticket_number} - {self.subject}'

# # Model for Ticket Messages (Conversation)
# class TicketMessage(models.Model):
#     ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
#     message = models.TextField(blank=False, null=False)
#     images = models.ImageField(upload_to='message_images/', blank=True, null=True)
#     audio = models.FileField(upload_to='message_audio/', blank=True, null=True)
#     documents = models.FileField(upload_to='message_documents/', blank=True, null=True)
#     sent_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Message from {self.user.username} on Ticket #{self.ticket.ticket_number}'



class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket')
    subject = models.CharField(max_length=500, blank=True, null=True)
    message = models.TextField(blank=False, null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='message_documents/')
    
class Gallary(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    title_bn = models.CharField(max_length=500, blank=False, null=False)
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='gallary_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Image uploaded at {self.time}'
    
class News(models.Model):
    title = models.CharField(max_length=555, blank=False, null=False)
    title_bn = models.CharField(max_length=555, blank=False, null=False)
    url = models.URLField(max_length=1000, blank=False, null=False)
    thumbnail = models.ImageField(upload_to='news_thumbnails/', blank=False, null=False, default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title