# import modules, classes and functions to build forms
from django.contrib.auth import get_user_model , forms#get current user model i.e customUser

from django.contrib.auth.forms import UserCreationForm, UserChangeForm #get usercreation and userchangeforms

from allauth.account.forms import LoginForm, ResetPasswordForm, ChangePasswordForm, ResetPasswordKeyForm, SignupForm

from django import forms


# Expose model fields for 'CustomUserCreationForm' and apply custom css styles
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "mail@example.com",})
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 'id' : 'exampleFormControlInput1', 'placeholder' : "",})
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'id' : 'exampleFormControlInput1', 'placeholder' : "",})

    def clean_email(self):
        data = self.cleaned_data['email']
        if get_user_model().objects.filter(email=data).exists():
            raise forms.ValidationError("This email has already been registered")
        return data

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'first_name', 'last_name',)

# Expose model fields for 'CustomUserChangeForm' and apply custom css styles
class CustomUserChangeForm(UserChangeForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({
            'type': 'file', 'id': 'file'})
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 'id' : 'exampleFormControlInput1', 'required': 'required'})
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "", 'required': 'required'})
        

    class Meta:
        model = get_user_model()
        fields = ('profile_picture','first_name', 'last_name', 'username', 'email',)




# Expose model fields for 'CustomAdminChangeForm'
class CustomAdminChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_role'].widget.attrs.update({'class': 'form-select', 'id': 'modifiedFormSelect' })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-check-input', 'id' : 'flexCheckDefault', 'type': 'checkbox',
        })
        # self.fields['is_active'].widget.attrs.update(checked='False')

    class Meta:
        model = get_user_model()
        fields = ( 'is_active', 'user_role')

# Expose model fields for 'CustomAdminEmailChangeForm'
class CustomAdminEmailChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_change_approved'].widget.attrs.update({
            'class': 'form-check-input', 'id' : 'flexCheckDefault', 'type': 'checkbox',
        })

    class Meta:
        model = get_user_model()
        fields = ( 'email_change_approved',)

# Apply custom css styles for 'CustomLoginForm'
class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",
        })
        self.fields['remember'].widget.attrs.update({
            'class': 'form-check-input', 'id' : 'flexCheckDefault', 'type': 'checkbox',
        })

# Apply custom css styles for 'CustomResetPasswordForm'
class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})

# Apply custom css styles for 'CustomChangePasswordForm'
class CustomChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})

# Apply custom css styles for 'CustomResetPasswordKeyForm'
class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "",})