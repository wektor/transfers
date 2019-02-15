from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from django.views.generic import TemplateView
from sharing import forms
from sharing import models

# Create your views here.


class UserAgentMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            user.user_agent = request.META.get('HTTP_USER_AGENT', '')
            user.save()
        return super().dispatch(request, *args, **kwargs)


class AddView(UserAgentMixin, LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'add.html'


class AddViewBase(UserAgentMixin, LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = None
    form = None
    title = "Add base"

    def get(self, request, *args, **kwargs):
        return render(request,
                      self.template_name,
                      {'title': self.title,
                       'form': self.form(),
                       }
                      )

    def post(self, request):
        post_form = self.form(request.POST, request.FILES)
        if not post_form.is_valid():
            return HttpResponse(post_form.errors)
        item = post_form.save(commit=False)
        new_url = models.SharedUrl(author=request.user)
        new_url.save()
        item.url = new_url
        item.save()
        return render(request,
                      'add_successful.html',
                      {'full_url': new_url.full_url,
                       'full_api_url': new_url.full_api_url,
                       'password': new_url.password,
                       }
                      )


class AddLink(AddViewBase):
    title = "Add link"
    template_name = 'add_item.html'
    form = forms.SharedLinkForm


class AddFile(AddViewBase):
    title = "Add file"
    template_name = 'add_item.html'
    form = forms.SharedFileForm


class OpenView(View):
    template_name = 'open.html'

    def get(self, request, url=None, **kwargs):
        shared_url = models.SharedUrl.objects.get(url=url)
        form = forms.OpenUrlForm(instance=shared_url)
        return render(request, self.template_name, {'form': form})

    def post(self, request, url=None):
        form = forms.OpenUrlForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        passwd = form.cleaned_data['password']
        shared_url = get_object_or_404(models.SharedUrl, url=url)
        if shared_url.check_password(passwd):
            if hasattr(shared_url, 'shared_link'):
                return redirect(shared_url.shared_link.link)
            if hasattr(shared_url, 'shared_file'):
                return redirect(shared_url.shared_file.file.url)
            else:
                print(repr(shared_url))
                return HttpResponseNotFound('No file or link connected to url')
        else:
            return render(request, self.template_name, {'form': form, 'invalid_password': True})
