# import modules to create filesystem forms 
from django.contrib.auth import get_user_model #get current user model i.e customUser

from django import forms

from .models import PublicFiles, PrivateFiles, Announcement

# Class to create form for single public file upload 
class PublicFilesCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput())
    
    def __init__(self,  *args, **kwargs):
        super(PublicFilesCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PublicFiles
        fields = [
            'filename', 'owner'
        ]

# Class to create form for directory upload 
class PublicFolderCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput(attrs=
        {'multiple': True, 'webkitdirectory': True, 'directory': True}))
    
    def __init__(self,  *args, **kwargs):
        super(PublicFolderCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder2', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PublicFiles
        fields = [
            'filename', 'owner'
        ]


# Class to create form for multiple public file upload 
class PublicFilesMultipleCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput(attrs=
        {'multiple': True}))
    
    def __init__(self,  *args, **kwargs):
        super(PublicFilesMultipleCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder1', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PublicFiles
        fields = [
            'filename', 'owner'
        ]

# Class to create form for public file update
class PublicFilesUpdateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput)

    def __init__(self,  *args, **kwargs):
        super(PublicFilesUpdateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'fileupdate', 'hidden': 'hidden'})
        

    
    class Meta:
        model = PublicFiles
        fields = [
            'filename',
        ]



# PRIVATE FILES/FOLDER UPLOAD SECTION

# Class to create form for single private file upload 
class PrivateFilesCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput())
    
    def __init__(self,  *args, **kwargs):
        super(PrivateFilesCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PrivateFiles
        fields = [
            'filename', 'owner'
        ]

# Class to create form for private folder upload 
class PrivateFolderCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput(attrs=
        {'multiple': True, 'webkitdirectory': True, 'directory': True}))
    
    def __init__(self,  *args, **kwargs):
        super(PrivateFolderCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder2', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PrivateFiles
        fields = [
            'filename', 'owner'
        ]


# Class to create form for multiple private  file upload 
class PrivateFilesMultipleCreateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput(attrs=
        {'multiple': True}))
    
    def __init__(self,  *args, **kwargs):
        super(PrivateFilesMultipleCreateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'uploadFolder1', 'hidden': 'hidden'})
        self.fields['owner'].widget.attrs.update({'class': 'form-control', 'hidden': 'hidden'})

    
    class Meta:
        model = PrivateFiles
        fields = [
            'filename', 'owner'
        ]


# Class to create form for private file update
class PrivateFilesUpdateForm(forms.ModelForm):
    filename = forms.FileField(required=False, widget=forms.FileInput)

    def __init__(self,  *args, **kwargs):
        super(PrivateFilesUpdateForm, self).__init__(*args, **kwargs)
        self.fields['filename'].widget.attrs.update({'class': 'form-control', 'id': 'fileupdate', 'hidden': 'hidden'})
        

    
    class Meta:
        model = PrivateFiles
        fields = [
            'filename',
        ]



# Class to create form for announcements
class AnnouncementForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "Enter the announcement title",})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'id': 'exampleFormControlInput1' , 'placeholder' : "Enter the announcement body",})
        self.fields['send_to'].widget.attrs.update({'class': 'form-select', 'id': 'modifiedFormSelect'})

    
    class Meta:
        model = Announcement
        fields = [
            'title', 'message', 'send_to',
        ]