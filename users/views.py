# import modules, classes and functions to create views
from django.shortcuts import render, HttpResponseRedirect, redirect

from django.http import JsonResponse

from django.core import serializers

from django.urls import reverse_lazy, reverse

from django.contrib.auth import get_user_model

from django.views.generic import DetailView, ListView, View

from django.views.generic.edit import UpdateView, DeleteView

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAdminEmailChangeForm,CustomAdminChangeForm

from .models import CustomUser 

from django.contrib.auth.mixins import ( LoginRequiredMixin)

from django.shortcuts import get_object_or_404

from django.db.models import Q


# function to check if request is an XMLHttpRequest
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# function to get all user objects to be rendered in frontend template
def user_list_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
        return render(request, template_name='errors/404.html', status=404)
    else:
        profiles = get_user_model().objects.all().order_by('first_name')
        context = {'profiles':profiles}
        return render(request, 'account/user_list.html' , context)

# function to get search result from user list
def user_search_results(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
        return render(request, template_name='errors/404.html', status=404)
    else:
        query = request.GET.get('userSearch')
        users = get_user_model().objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        context = {'users':users}
        return render(request, 'account/user_search_list.html' , context)


# function to set is_custom_admin = True on switch toggle in frontend template
def set_admin(request, pk):
    if is_ajax(request=request) and request.method=='POST':
        # print(request)
        print(request.user)
        print(pk)
        profile = get_user_model().objects.get(id=pk)
        print(request.POST.get('my_id'))
        
        profile.is_custom_admin = True if request.POST.get('is_custom_admin') == 'true' else False
        profile.save()
        data = {'status':'success', 'is_custom_admin':profile.is_custom_admin}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)


# function to delete profile picture on "delete" button click in frontend template
def delete_profile_picture(request, pk):
    if is_ajax(request=request) and request.method == 'POST':
        profile = get_user_model().objects.get(id=pk)
        profile.profile_picture = None
        profile.save()
        data = {'status': 'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status': 'error'}
        return JsonResponse(data, status=400)


# function to request email change on "request email change" button click
def request_email_change(request, pk):
    if is_ajax(request=request) and request.method == 'POST':
        profile = get_user_model().objects.get(id=pk)
        profile.email_change_requested = True
        profile.save()
        data = {'status': 'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status': 'error'}
        return JsonResponse(data, status=400)




# view to display registered users
class RegistrationListView(ListView):
    model = get_user_model()
    template_name = 'account/reg_list.html'
    context_object_name = 'reg_list'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)

# view to display search results on registered users
class RegistrationSearchListView(ListView):
    model = get_user_model()
    context_object_name = 'reg_list'
    template_name = 'account/reg_search_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get('regSearch')
        return get_user_model().objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))


# view to display list of users that have requested for email change
class EmailChangeListView(ListView):
    model = get_user_model()
    template_name = 'account/email_change_list.html'
    context_object_name = 'email_list'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)


# view to show user details
class UserDetailView(DetailView):
    model = get_user_model()
    context_object_name = 'user'
    template_name = 'account/user_detail.html'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)


#  view to enable users update parameters 
class UserUpdateView(View):
    model = get_user_model()
    template_name = 'account/edit_user.html'
    form_class = CustomUserChangeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            pk = self.kwargs['pk']
            user = get_object_or_404(self.model, pk=pk)
            user.email_change_approved = False
            user.save()
            form = self.form_class(self.request.POST, self.request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('user_detail', user.id)
            else:
                form = self.form_class()
        return  redirect('user_detail', user.id)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(self.model, pk=pk)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'user': user})



# view to enable admin perform operations on the users
class AdminUpdateView(View):
    model = get_user_model()
    template_name = 'account/admin_edit.html'
    form_class = CustomAdminChangeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            pk = self.kwargs['pk']
            user = get_object_or_404(self.model, pk=pk)
            form = self.form_class(self.request.POST, instance=user)
            if form.is_valid():
                form.save()
                # return redirect('user_detail', user.id)
                return redirect('reg_list')
            else:
                form = self.form_class()
        return  redirect('reg_list')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(self.model, pk=pk)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'user': user})


# view to enable admins grant permission to users to update their email
class AdminUpdateEmailView(View):
    model = get_user_model()
    template_name = 'account/admin_edit_email.html'
    form_class = CustomAdminEmailChangeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            pk = self.kwargs['pk']
            user = get_object_or_404(self.model, pk=pk)
            user.email_change_requested = False
            user.save()
            form = self.form_class(self.request.POST, instance=user)
            
            if form.is_valid():
                form.save()
                return redirect('email_list')
            else:
                form = self.form_class()
        return  redirect('email_list')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(self.model, pk=pk)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'user': user})


# view to enable admin delete users
class UserDeleteView(DeleteView):
    model = get_user_model()
    template_name = 'account/delete_user.html'
    success_url = reverse_lazy('user_list')
    context_object_name = 'user'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        elif not (request.user.is_custom_admin or request.user.user_role == 'manager'):
            return render(request, template_name='errors/404.html', status=404)
        else:
            return super().dispatch(request, *args, **kwargs)
