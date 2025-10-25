import os
import mimetypes
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_http_methods


@cache_control(max_age=86400)  # Cache for 24 hours
@require_http_methods(["GET", "HEAD"])
def serve_media(request, path):
    """
    Custom media file serving view for production
    """
    # Security: prevent directory traversal
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    
    # Construct full file path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")
    
    # Security: ensure file is within MEDIA_ROOT
    if not os.path.abspath(file_path).startswith(os.path.abspath(settings.MEDIA_ROOT)):
        raise Http404("Invalid path")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Return file response
    try:
        return FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=False
        )
    except IOError:
        raise Http404("File not found")