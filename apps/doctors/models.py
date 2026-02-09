from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Specialization(models.Model):
    """Medical Specialization"""

    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('specialization')
        verbose_name_plural = _('specializations')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Prefer English name for slug since slugify doesn't handle Arabic well
            name_for_slug = getattr(self, 'name_en', '') or getattr(self, 'name_ar', '') or self.name
            if name_for_slug:
                from django.utils.text import slugify as django_slugify
                base_slug = django_slugify(name_for_slug)
                # If slugify returns empty (Arabic text), use a fallback
                if not base_slug:
                    base_slug = f"specialization-{self.pk or 'new'}"
                    
                slug = base_slug
                counter = 1
                while Specialization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
        super().save(*args, **kwargs)


class Doctor(models.Model):
    """Doctor Profile"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name=_('user')
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name=_('clinic')
    )
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.PROTECT,
        related_name='doctors',
        verbose_name=_('specialization')
    )

    # Professional Info
    license_number = models.CharField(_('license number'), max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(_('years of experience'), default=0)
    education = models.TextField(_('education'), blank=True)
    bio = models.TextField(_('biography'))

    # Consultation
    consultation_fee = models.DecimalField(
        _('consultation fee'),
        max_digits=10,
        decimal_places=2,
        default=0.0
    )

    # Stats
    total_patients = models.PositiveIntegerField(_('total patients'), default=0)
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    total_reviews = models.PositiveIntegerField(_('total reviews'), default=0)

    # Status
    is_available = models.BooleanField(_('available'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('doctor')
        verbose_name_plural = _('doctors')
        ordering = ['-rating', 'user__first_name']
        indexes = [
            models.Index(fields=['clinic', 'specialization']),
            models.Index(fields=['-rating']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class WorkingHour(models.Model):
    """Doctor's Weekly Schedule"""

    DAYS_OF_WEEK = [
        (0, _('Sunday')),
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
        (6, _('Saturday')),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='working_hours',
        verbose_name=_('doctor')
    )
    day_of_week = models.IntegerField(_('day of week'), choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('working hour')
        verbose_name_plural = _('working hours')
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"


class DayOff(models.Model):
    """Doctor's Days Off / Holidays"""

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='days_off',
        verbose_name=_('doctor')
    )
    date = models.DateField(_('date'))
    reason = models.CharField(_('reason'), max_length=200, blank=True)
    is_recurring = models.BooleanField(_('recurring annually'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('day off')
        verbose_name_plural = _('days off')
        unique_together = ['doctor', 'date']
        ordering = ['date']
        indexes = [
            models.Index(fields=['doctor', 'date']),
        ]

    def __str__(self):
        return f"{self.doctor} - {self.date}"
