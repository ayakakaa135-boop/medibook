# ============================================
# clinics/models.py
# ============================================
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Clinic(models.Model):
    """Medical Clinic Model"""

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True, blank=True)
    description = models.TextField(_('description'))
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    phone = models.CharField(_('phone'), max_length=20)
    email = models.EmailField(_('email'))
    website = models.URLField(_('website'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='clinics/logos/', blank=True)
    cover_image = models.ImageField(_('cover image'), upload_to='clinics/covers/', blank=True)

    # Operating hours
    opening_time = models.TimeField(_('opening time'), default='08:00')
    closing_time = models.TimeField(_('closing time'), default='20:00')

    # Meta
    is_active = models.BooleanField(_('active'), default=True)
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    total_reviews = models.PositiveIntegerField(_('total reviews'), default=0)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('clinic')
        verbose_name_plural = _('clinics')
        ordering = ['-rating', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['city']),
            models.Index(fields=['-rating']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Clinic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

