from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class ROLE_CHOICES(models.TextChoices):
        ADMIN = "admin"
        TRAINER = "trainer"
        MEMBER = "member"

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CHOICES.MEMBER)

    def __str__(self):
        return f"{self.username} ({self.role})"


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_month = models.PositiveIntegerField()
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} {self.duration_month} months - ${self.fee}"


class Trainer(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                related_name="trainer_profile", null=True)
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    shift_timing = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.specialization}"


class MemberProfile(models.Model):

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'.")
    class GENDER_CHOICES(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        OTHER = "Other"
    
    full_name = models.CharField(max_length=100)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="member_profile",
        on_delete=models.CASCADE,
    )
    mobile = models.CharField(max_length=20,validators=[phone_regex])
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=GENDER_CHOICES.MALE)
    address = models.TextField(null=True)
    join_date = models.DateField(default=timezone.now ,db_index=True)
    plan = models.ForeignKey(
        MembershipPlan,
        related_name="members",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    membership_start = models.DateField(null=True, blank=True)
    membership_end = models.DateField(null=True, blank=True)
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trainees",
    )

    def __str__(self):
        return f"{self.full_name} - {self.user.username} - Plan : {self.plan.name if self.plan else 'No Plan'}"


class Equipment(models.Model):
    name = models.CharField(max_length=50)
    units = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True ,db_index=True)

    def __str__(self):
        return f"{self.name} (Units:{self.units})"


class Payment(models.Model):
    class PAYMENT_METHOD_CHOCIES(models.TextChoices):
        CASH='Cash'
        ONLINE='Online Transfer'

    class PAYMENT_STATUS_CHOICE(models.TextChoices):
        PENDING= 'Pending'
        PAID='Paid'
        FAILED='Failed'
    member=models.ForeignKey(MemberProfile, related_name='payments', on_delete=models.CASCADE)
    plan =models.ForeignKey(MembershipPlan, related_name='plan',null=True,blank=True, on_delete=models.SET_NULL)
    amount=models.DecimalField( max_digits=8, decimal_places=2)
    payment_date=models.DateTimeField( default=timezone.now ,db_index=True)
    Payment_method=models.CharField( max_length=20,choices=PAYMENT_METHOD_CHOCIES)
    Payment_status=models.CharField( max_length=20,choices=PAYMENT_STATUS_CHOICE,default=PAYMENT_STATUS_CHOICE.PENDING)

    def __str__(self):
        return f"Payment of ${self.amount} by {self.member.full_name} on {self.payment_date}"




class Attendance(models.Model):
    member=models.ForeignKey(MemberProfile,
         on_delete=models.CASCADE ,related_name='Attendances')

    date=models.DateField(default=timezone.now)
    time_in=models.TimeField(null=True,blank=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['member', 'date'], name='unique_member_attendance_per_day'),
        )

    def __str__(self):
        return f"{self.member.full_name} - {self.date} - {self.time_in}"


class Enquiry(models.Model):
    class ENQUIRY_STATUS_CHOICES(models.TextChoices):
        NEW='New'
        SEEN='Seen'
        RESOLVED='Resolved'
        
        
    name=models.CharField( max_length=100)
    email=models.EmailField()
    mobile=models.CharField(max_length=20)
    message=models.TextField()
    status = models.CharField(max_length=20, choices=ENQUIRY_STATUS_CHOICES.choices, default=ENQUIRY_STATUS_CHOICES.NEW)
    created_at=models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.name} - {self.email}"


class WorkPlan(models.Model):
    member=models.ForeignKey(MemberProfile,
                on_delete=models.CASCADE,
                related_name='workout_plans',)
    title=models.CharField( max_length=100)
    description=models.TextField(blank=True)
    created_at=models.DateField( auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Created at: {self.created_at}"


class Feedback(models.Model):
    member=models.ForeignKey(MemberProfile,
                on_delete=models.CASCADE,
                related_name='feedback',)
    message=models.TextField()
    created_at=models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return f"feedback from {self.member.full_name} - created at : {self.created_at}"