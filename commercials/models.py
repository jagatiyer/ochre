from django.db import models


class CommercialVideo(models.Model):
	title = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	# Upload a video file (mp4/etc) OR provide an embed URL (direct mp4 URL)
	video = models.FileField(upload_to='commercials/videos/', blank=True, null=True)
	# Optional embed fields: either `embed_url` (direct video URL) or `embed_html` (iframe/embed code)
	embed_url = models.CharField(max_length=800, blank=True)
	embed_html = models.TextField(blank=True)
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('order',)

	def __str__(self):
		return self.title or f"CommercialVideo {self.pk}"

	@property
	def embed_type(self):
		"""Return one of: 'html', 'youtube', 'vimeo', 'direct', 'upload', or None."""
		if self.embed_html:
			return 'html'
		if self.embed_url:
			url = self.embed_url.lower()
			if 'youtube.com' in url or 'youtu.be' in url:
				return 'youtube'
			if 'vimeo.com' in url:
				return 'vimeo'
			if url.endswith(('.mp4', '.webm', '.ogg')):
				return 'direct'
			return 'direct'
		if self.video:
			return 'upload'
		return None

	@property
	def embed_src(self):
		"""Return the normalized src for iframe or video sources.

		For YouTube/Vimeo returns an embeddable player URL; for direct/upload returns the media URL.
		"""
		if self.embed_html:
			return None
		t = self.embed_type
		if t == 'youtube':
			url = self.embed_url
			# Extract video id (simple heuristics)
			if 'v=' in url:
				vid = url.split('v=')[-1].split('&')[0]
			elif 'youtu.be/' in url:
				vid = url.split('youtu.be/')[-1].split('?')[0]
			else:
				vid = url
			return f'https://www.youtube.com/embed/{vid}'
		if t == 'vimeo':
			url = self.embed_url
			vid = url.rstrip('/').split('/')[-1]
			return f'https://player.vimeo.com/video/{vid}'
		if t == 'direct':
			return self.embed_url
		if t == 'upload':
			try:
				return self.video.url
			except Exception:
				return None
		return None
