# apps/departments/decorators.py
from functools import wraps
from django.shortcuts import render
from django.utils import timezone
from .models import DepartmentPortalConfig

def departments_open_required(viewfunc):
    @wraps(viewfunc)
    def _wrapped(request, *args, **kwargs):
        cfg = DepartmentPortalConfig.get_solo()
        if not cfg.is_effectively_open:
            # Show a friendly “closed” page; use 403 to avoid indexing
            return render(
                request,
                "closed.html",
                {"config": cfg, "now": timezone.now()},
                status=403,
            )
        return viewfunc(request, *args, **kwargs)
    return _wrapped
