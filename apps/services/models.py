from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Service(models.Model):
    """Medical Service offered by clinic"""

    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('clinic')
    )
    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), blank=True)
    description = models.TextField(_('description'))
    duration_minutes = models.PositiveIntegerField(_('duration (minutes)'), default=30)
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        default=0.0
    )

    # Requirements
    requires_fasting = models.BooleanField(_('requires fasting'), default=False)
    preparation_instructions = models.TextField(
        _('preparation instructions'),
        blank=True
    )

    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ['clinic', 'name']
        unique_together = ['clinic', 'slug']

    def __str__(self):
        return f"{self.clinic.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Prefer English name for slug since slugify doesn't handle Arabic well
            name_for_slug = getattr(self, 'name_en', '') or getattr(self, 'name_ar', '') or self.name
            if name_for_slug:
                base_slug = slugify(name_for_slug)
                # If slugify returns empty (Arabic text), use a fallback
                if not base_slug:
                    base_slug = f"service-{self.pk or 'new'}"
                    
                slug = base_slug
                counter = 1

                while Service.objects.filter(
                        clinic=self.clinic,
                        slug=slug
                ).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                self.slug = slug

        super().save(*args, **kwargs)


