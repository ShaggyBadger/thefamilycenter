from django.db import models
from django.utils import timezone


class ContactSubmission(models.Model):
    """Minimal general inquiry retained only for the approved retention period."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "contact inquiry"
        verbose_name_plural = "contact inquiries"

    def __str__(self):
        return f"Inquiry from {self.name} ({self.created_at:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        if self.is_resolved and self.resolved_at is None:
            self.resolved_at = timezone.now()
        elif not self.is_resolved:
            self.resolved_at = None
        super().save(*args, **kwargs)
