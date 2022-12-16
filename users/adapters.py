from django.shortcuts import resolve_url
from allauth.account.adapter import DefaultAccountAdapter


# Modify 'get_email_confirmation_redirect_url' method of dj allauth adapter 
# to redirect to 'account_inactive' url on email confirmation.
class ModifiedAccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_redirect_url(self, request):
        """
        The URL to return to after successful e-mail confirmation.
        """
        return resolve_url('account_inactive')

