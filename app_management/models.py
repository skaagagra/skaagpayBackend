from django.db import models

class AppVersion(models.Model):
    version_name = models.CharField(max_length=50) # e.g. "1.0.1"
    version_code = models.IntegerField(unique=True) # e.g. 2
    apk_file = models.FileField(upload_to='apks/')
    release_notes = models.TextField(blank=True, null=True)
    is_force_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Version {self.version_name} ({self.version_code})"

    class Meta:
        ordering = ['-version_code']
