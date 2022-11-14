# import modules, classes and functions to create views
from django.shortcuts import render, HttpResponseRedirect, redirect

from django.urls import reverse_lazy, reverse

from django.contrib.auth import get_user_model

from django.views.generic import DetailView, ListView, View

from django.views.generic.edit import UpdateView, DeleteView

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAdminChangeForm, CustomEmailChangeForm

from .models import CustomUser #EmailRequest

from django.contrib.auth.mixins import ( LoginRequiredMixin)
from django.shortcuts import get_object_or_404

#  view to display list of existing users
class UserListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'account/user_list.html'
    context_object_name = 'user_list'

# view to display registered users
class RegistrationListView(ListView):
    model = get_user_model()
    template_name = 'account/reg_list.html'
    context_object_name = 'reg_list'

# view to show user details
class UserDetailView(DetailView):
    model = get_user_model()
    context_object_name = 'user'
    template_name = 'account/user_detail.html'
    pk_url_kwarg = 'pk'

#  view to enable users update parameters 
class UserUpdateView(UpdateView):
    model = get_user_model()
    template_name = 'account/edit_user.html'
    form_class = CustomUserChangeForm

# class UserRequestEmailChange(View):
#     template_name = 'account/user_edit_email.html'
#     model = get_user_model()
#     form_class = CustomEmailChangeForm

#     # def post(self,request, *args, **kwargs):
#     #     pk = self.kwargs['pk']
#     #     req = get_object_or_404(EmailRequest, pk=pk)
#     #     user = get_object_or_404(self.model, pk=req.user.id)
#     #     user.email_change_requested = False
#     #     user.save(update_fields=['email_change_requested'])
#     #     req.status = 'confirmed'
#     #     req.save(update_fields=['status'])

#     def post(self,request, *args, **kwargs):
#         pk = self.kwargs['pk']
#         user = get_object_or_404(self.model, pk=pk)
#         request = EmailRequest(user=user)
#         request.save()
#         # form = self.form_class()
#         # if form.is_valid():
#             # <process form cleaned data>
#         return HttpResponseRedirect(reverse('account_logout'))


#         # return render(request, self.template_name, {'form': form})

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

# class AdminRequestEmailChange(View):
#     template_name = 'account/admin_edit_email.html'
#     model = get_user_model()
#     form_class = CustomEmailChangeForm

#     def post(self,request, *args, **kwargs):
#         pk = self.kwargs['pk']
#         req = get_object_or_404(EmailRequest, pk=pk)
#         user = get_object_or_404(self.model, pk=req.user.id)
#         user.email_change_requested = False
#         user.save(update_fields=['email_change_requested'])
#         req.status = 'confirmed'
#         req.save(update_fields=['status'])

#     # def post(self,request, *args, **kwargs):
#     #     pk = self.kwargs['pk']
#     #     user = get_object_or_404(self.model, pk=pk)
#     #     request = EmailRequest(user=user)
#     #     request.save()

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})



# view to enable admin perform operations on the users
class AdminUpdateView(UpdateView):
    model = get_user_model()
    template_name = 'account/admin_edit.html'
    form_class = CustomAdminChangeForm

#  view to enable admin deactivate users 
class DeactivateUserUpdateView(UpdateView):
    model = get_user_model()
    template_name = 'account/deactivate_user.html'
    form_class = CustomAdminChangeForm

# view to enable admin delete users
class UserDeleteView(DeleteView):
    model = get_user_model()
    template_name = 'account/delete_user.html'
    success_url = reverse_lazy('home')
    context_object_name = 'user'
