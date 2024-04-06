from django.urls import reverse_lazy

from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

class Indexview(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "index.html"

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)