# import modules, classes and functions to create views
from django.shortcuts import render
from .models import (PublicFiles, SharedFiles, PublicFolders, SharedFolders, PrivateFiles, PrivateFolders, 
                     SharedPrivateFiles, SharedPrivateFolders, Announcement)
from notification.models import Notification
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from .forms import (PublicFilesCreateForm, PublicFilesUpdateForm, PublicFilesMultipleCreateForm,
                     PublicFolderCreateForm, PrivateFilesCreateForm, PrivateFilesMultipleCreateForm,
                     PrivateFolderCreateForm, PrivateFilesUpdateForm, AnnouncementForm)
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.mixins import ( LoginRequiredMixin)
from secrets import token_hex
import random
import os, json
from itertools import chain
import pandas as pd
from plotly.offline import plot
import plotly.express as px



# Create your views here.

# function to check if request is ajax request
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'  

# function to display all users on shared list of a specific file
def shared_with_view(request):
        file_id = request.GET.get("file_id")
        if file_id:
            try:
                file = PublicFiles.objects.get(id=file_id)
                fileshared = SharedFiles.objects.filter(filename=file)
            except:
                file = PrivateFiles.objects.get(id=file_id)
                fileshared = SharedPrivateFiles.objects.filter(filename=file)
        else:
            fileshared = None
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/shared_user_list_result_partial.html", 
                context={ 'sharedfile': fileshared}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, 'filesystem/file_list.html')

# function to remove users from shared list on specific files
def delete_shared_user_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        shared_user = request.POST.get('shared_user')
        try:
            file = PublicFiles.objects.get(id=file_id)
            fileshared = SharedFiles.objects.filter(filename=file)
        except:
            file = PrivateFiles.objects.get(id=file_id)
            fileshared = SharedPrivateFiles.objects.filter(filename=file)
        user = get_user_model().objects.get(id=shared_user)
        for f in fileshared:
            if f.user == user:
                f.delete()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)


# function to create folder for multiple files/directory uploads
def create_folder_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.POST.get('createFolder')
        folder = PublicFolders(folder_name=query, owner=request.user)
        folder.save()
        return redirect('folder_detail', folder.id)  

# function to share single or multiple files with single or multiple users
def share_file_view(request):
    if is_ajax(request=request) and request.method=='POST':
        checkboxes = request.POST.getlist('myCheckboxes[]')
        users = request.POST.getlist('myUsers[]')
        permission_values = request.POST.getlist('myUsersPermissions[]')
        file_id = request.POST.get('file_id')
        if len(checkboxes) > 0:
            for x in checkboxes:
                for y in range(len(users)):
                    try:
                        file_name = PublicFiles.objects.get(id=x)
                    except:
                        file_name = PrivateFiles.objects.get(id=x)
                    user = get_user_model().objects.get(id=users[y])
                    permission = permission_values[y]
                    try:
                        share = SharedFiles(filename=file_name, user=user, permission_field=permission)
                        Notification.objects.create(notification_type=1, to_user=user, from_user=request.user, publicfile=file_name)
                    except:
                        share = SharedPrivateFiles(filename=file_name, user=user, permission_field=permission)
                        Notification.objects.create(notification_type=1, to_user=user, from_user=request.user, privatefile=file_name)
                    share.save()
            data = {'status':'success'}
            return JsonResponse(data, status=200)
        else:
            for y in range(len(users)):
                try:
                    file_name = PublicFiles.objects.get(id=file_id)
                except:
                    file_name = PrivateFiles.objects.get(id=file_id) 
                user = get_user_model().objects.get(id=users[y])
                permission = permission_values[y]
                try:
                    share = SharedFiles(filename=file_name, user=user, permission_field=permission)
                    Notification.objects.create(notification_type=1, to_user=user, from_user=request.user, publicfile=file_name)
                except:
                    share = SharedPrivateFiles(filename=file_name, user=user, permission_field=permission)
                    Notification.objects.create(notification_type=1, to_user=user, from_user=request.user, privatefile=file_name)
                share.save()
            data = {'status':'success'}
            return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to rename file with text input from request object
def rename_file_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        rename_input = request.POST.get('rename_input')
        file_root, file_ext = os.path.splitext(rename_input)
        my_chars = token_hex(2)
        rename_input = file_root + '_' + str(my_chars) + file_ext
        try:
            file_instance = PublicFiles.objects.get(id=file_id)
            old_file_name = str(file_instance.filename)
            # Notification.objects.create(notification_type=3, to_user=file_instance.owner, from_user=request.user, publicfile=file_instance, old_file_name=old_file_name )
        except:
            file_instance = PrivateFiles.objects.get(id=file_id)
            old_file_name = str(file_instance.filename)
            # Notification.objects.create(notification_type=3, to_user=file_instance.owner, from_user=request.user, privatefile=file_instance, old_file_name=old_file_name )
        os.rename(file_instance.filename.path, settings.MEDIA_ROOT + '/' + rename_input)
        file_instance.filename = rename_input
        file_instance.save()
        try:
            Notification.objects.create(notification_type=3, to_user=file_instance.owner, from_user=request.user, publicfile=file_instance, old_file_name=old_file_name )
        except:
            Notification.objects.create(notification_type=3, to_user=file_instance.owner, from_user=request.user, privatefile=file_instance, old_file_name=old_file_name )
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to edit file permission   
def edit_permission_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        permission_value = request.POST.get('permission_value')
        try:
            file_instance = PublicFiles.objects.get(id=file_id)
        except:
            file_instance = PrivateFiles.objects.get(id=file_id)
        file_instance.permission_field = permission_value
        file_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to set recycled flag on file instance to true    
def recycle_file_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        try:
            file_instance = PublicFiles.objects.get(id=file_id)
        except:
            file_instance = PrivateFiles.objects.get(id=file_id)
        file_instance.recycled = True
        file_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to search for specific file using filename as query
def file_search_view(request):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            query = request.GET.get('publicFilesSearch')
            file_list = PublicFiles.objects.filter(Q(filename__icontains=query))
            # print(file_list)
            context = {'file_list': file_list}
            return render(request, 'filesystem/search_file_list.html' , context)
    
# function to sort file by file type i.e pdf, docx, xlsx etc
def sort_file_view(request):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            query = request.GET.get('sortInput')
            if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
                file_list = PublicFiles.objects.filter(Q(filename__icontains=query))
            elif query == 'photos':
                file_list = PublicFiles.objects.filter(Q(filename__icontains='jpg') | Q(filename__icontains='png') | Q(filename__icontains='jpeg'))
            else:
                file_list = PublicFiles.objects.filter(Q(filename__icontains='mpeg') | Q(filename__icontains='mp4') | Q(filename__icontains='mkv') | Q(filename__icontains='mov'))
            context = {'file_list': file_list}
            return render(request, 'filesystem/sort_file_list.html' , context)


# function to search for specific file using filename as query(GRID VIEW)
def file_search_grid_view(request):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            query = request.GET.get('publicFilesSearch')
            file_list = PublicFiles.objects.filter(Q(filename__icontains=query))
            context = {'file_list': file_list}
            return render(request, 'filesystem/search_file_grid.html' , context)

# function to sort file by file type i.e pdf, docx, xlsx etc (GRID VIEW)
def sort_file_grid_view(request):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            query = request.GET.get('sortInput')
            if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
                file_list = PublicFiles.objects.filter(Q(filename__icontains=query))
            elif query == 'photos':
                file_list = PublicFiles.objects.filter(Q(filename__icontains='jpg') | Q(filename__icontains='png') | Q(filename__icontains='jpeg'))
            elif query == 'date':
                file_list = PublicFiles.objects.all().order_by('date')
            elif query == 'ascending':
                file_list = PublicFiles.objects.all().order_by('filename')
            elif query == 'descending':
                file_list = PublicFiles.objects.all().order_by('-filename')
            else:
                file_list = PublicFiles.objects.filter(Q(filename__icontains='mpeg') | Q(filename__icontains='mp4') | Q(filename__icontains='mkv') | Q(filename__icontains='mov'))
            context = {'file_list': file_list}
            return render(request, 'filesystem/sort_file_grid.html' , context)

# function to upload multiple files to a folder
def multiple_file_upload_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        form = PublicFilesMultipleCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PublicFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('folder_detail', folder.id)
        else:
            form = PublicFilesMultipleCreateForm()
        return redirect('folder_detail', folder.id)

# function to upload contents of a directory on local machine to folder on digital library
def directory_upload_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        form = PublicFolderCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PublicFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('folder_detail', folder.id)
        else:
            form = PublicFolderCreateForm()
        return redirect('folder_detail', folder.id)

# function to share single or multiple folders with single or multiple users
def share_folder_view(request):
    if is_ajax(request=request) and request.method=='POST':
        checkboxes = request.POST.getlist('myCheckboxes[]')
        users = request.POST.getlist('myUsers[]')
        permission_values = request.POST.getlist('myUsersPermissions[]')
        folder_id = request.POST.get('file_id')
        if len(checkboxes) > 0:
            for x in checkboxes:
                for y in range(len(users)):
                    try:
                        folder_name = PublicFolders.objects.get(id=x)
                    except:
                        folder_name = PrivateFolders.objects.get(id=x)
                    user = get_user_model().objects.get(id=users[y])
                    permission = permission_values[y]
                    try:
                        share = SharedFolders(folder_name=folder_name, user=user, permission_field=permission)
                        Notification.objects.create(notification_type=2, to_user=user, from_user=request.user, publicfolder=folder_name)
                    except:
                        share = SharedPrivateFolders(folder_name=folder_name, user=user, permission_field=permission)
                        Notification.objects.create(notification_type=2, to_user=user, from_user=request.user, privatefolder=folder_name)
                    share.save()
            data = {'status':'success'}
            return JsonResponse(data, status=200)
        else:
            for y in range(len(users)):
                try:
                    folder_name = PublicFolders.objects.get(id=folder_id)
                except:
                    folder_name = PrivateFolders.objects.get(id=folder_id)
                user = get_user_model().objects.get(id=users[y])
                permission = permission_values[y]
                try:
                    share = SharedFolders(folder_name=folder_name, user=user, permission_field=permission)
                    Notification.objects.create(notification_type=2, to_user=user, from_user=request.user, publicfolder=folder_name)
                except:
                    share = SharedPrivateFolders(folder_name=folder_name, user=user, permission_field=permission)
                    Notification.objects.create(notification_type=2, to_user=user, from_user=request.user, privatefolder=folder_name)
                share.save()
            data = {'status':'success'}
            return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to rename folder with text input from request object
def rename_folder_view(request):
    if is_ajax(request=request) and request.method=='POST':
        folder_id = request.POST.get('file_id')
        rename_input = request.POST.get('rename_input')
        try:
            folder_instance = PublicFolders.objects.get(id=folder_id)
            old_folder_name = str(folder_instance.folder_name)
            Notification.objects.create(notification_type=4, to_user=folder_instance.owner, from_user=request.user, publicfolder=folder_instance, old_folder_name=old_folder_name )
        except:
            folder_instance = PrivateFolders.objects.get(id=folder_id)
            old_folder_name = str(folder_instance.folder_name)
            Notification.objects.create(notification_type=4, to_user=folder_instance.owner, from_user=request.user, privatefolder=folder_instance, old_folder_name=old_folder_name )
        folder_instance.folder_name = rename_input
        folder_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to edit folder permission   
def edit_folder_permission_view(request):
    if is_ajax(request=request) and request.method=='POST':
        folder_id = request.POST.get('file_id')
        permission_value = request.POST.get('permission_value')
        try:
            folder_instance = PublicFolders.objects.get(id=folder_id)
        except:
            folder_instance = PrivateFolders.objects.get(id=folder_id)
        folder_instance.permission_field = permission_value
        folder_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to set recycled flag on folder instance to true    
def recycle_folder_view(request):
    if is_ajax(request=request) and request.method=='POST':
        folder_id = request.POST.get('file_id')
        try:
            folder_instance = PublicFolders.objects.get(id=folder_id)
        except:
            folder_instance = PrivateFolders.objects.get(id=folder_id)
        folder_instance.recycled = True
        folder_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to display all users on shared list of a specific folder
def folder_shared_with_view(request):
        file_id = request.GET.get("file_id")
        if file_id:
            try:
                file = PublicFolders.objects.get(id=file_id)
                fileshared = SharedFolders.objects.filter(folder_name=file)
            except:
                file = PrivateFolders.objects.get(id=file_id)
                fileshared = SharedPrivateFolders.objects.filter(folder_name=file)
        else:
            fileshared = None
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/shared_user_list_result_partial.html", 
                context={ 'sharedfile': fileshared}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, 'filesystem/folder_list.html')

# function to remove users from shared list on specific folders
def folder_delete_shared_user_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        shared_user = request.POST.get('shared_user')
        try:
            file = PublicFolders.objects.get(id=file_id)
            fileshared = SharedFolders.objects.filter(folder_name=file)
        except:
            file = PrivateFolders.objects.get(id=file_id)
            fileshared = SharedPrivateFolders.objects.filter(folder_name=file)
        user = get_user_model().objects.get(id=shared_user)
        for f in fileshared:
            if f.user == user:
                f.delete()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to search for specific folder using folder_name as query
def folder_search_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list = PublicFolders.objects.filter(Q(folder_name__icontains=query))
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/search_folder_list.html' , context)

# function to display files within specific folder
def folder_detail_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        try:
            shared_folder = SharedFolders.objects.get(Q(folder_name=folder) & Q(user=request.user))
        except:
            shared_folder = None
        associated_files = PublicFiles.objects.filter(folder=folder)
        form1 = PublicFilesMultipleCreateForm(initial={'owner': request.user})
        form2 = PublicFolderCreateForm(initial={'owner': request.user})
        context = {'file_list': associated_files, 'form1': form1, 'form2': form2, 'folder': folder, 'shared_folder': shared_folder}
        return render(request, 'filesystem/folder_detail.html' , context)

# function to upload multiple files to specific folder(GRID VIEW)
def multiple_file_upload_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        form = PublicFilesMultipleCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PublicFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('folder_detail_grid', folder.id)
        else:
            form = PublicFilesMultipleCreateForm()
        return redirect('folder_detail_grid', folder.id)

# function to upload directory contents to specific folder in digital library(GRID VIEW)
def directory_upload_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        form = PublicFolderCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PublicFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('folder_detail_grid', folder.id)
        else:
            form = PublicFolderCreateForm()
        return redirect('folder_detail_grid', folder.id)

# function to search for specific folder using folder_name as query(GRID VIEW)
def folder_search_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list = PublicFolders.objects.filter(Q(folder_name__icontains=query))
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/search_folder_grid.html' , context)

# function to sort folder by name and date created (GRID VIEW)
def sort_folder_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'date':
            folder_list = PublicFolders.objects.all().order_by('date')
        elif query == 'ascending':
            folder_list = PublicFolders.objects.all().order_by('folder_name')
        else:
            folder_list = PublicFolders.objects.all().order_by('-folder_name')
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/sort_folder_grid.html' , context)

# function to list files within specific folders (GRID VIEW)
def folder_detail_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PublicFolders.objects.get(id=pk)
        try:
            shared_folder = SharedFolders.objects.get(Q(folder_name=folder) & Q(user=request.user))
        except:
            shared_folder = None
        associated_files = PublicFiles.objects.filter(folder=folder)
        form1 = PublicFilesMultipleCreateForm(initial={'owner': request.user})
        form2 = PublicFolderCreateForm(initial={'owner': request.user})
        context = {'file_list': associated_files, 'form1': form1, 'form2': form2, 'folder': folder, 'shared_folder': shared_folder}
        return render(request, 'filesystem/folder_detail_grid.html' , context)

# function to search for specific file in shared files using filename as query
def shared_file_search_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFilesSearch')
        file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains=query))
        file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
        file_list = chain(file_list1, file_list2)
        context = {'file_list': file_list}
        return render(request, 'filesystem/search_shared_file_list.html' , context)

# function to sort file in shared files by file type i.e pdf, docx, xlsx etc
def sort_shared_file_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains=query))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
            file_list = chain(file_list1, file_list2)
        elif query == 'photos':
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
            file_list = chain(file_list1, file_list2)
        else:
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
            file_list = chain(file_list1, file_list2)
        context = {'file_list': file_list}
        return render(request, 'filesystem/sort_shared_file_list.html' , context)

# function to search for specific file in shared files using filename as query(GRID VIEW)
def shared_file_search_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFilesSearch')
        file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains=query))
        file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
        file_list = chain(file_list1, file_list2)
        context = {'file_list': file_list}
        return render(request, 'filesystem/search_shared_file_grid.html' , context)

# function to sort file in shared files by file type i.e pdf, docx, xlsx etc(GRID VIEW)
def sort_shared_file_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains=query))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
            file_list = chain(file_list1, file_list2)
        elif query == 'photos':
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
            file_list = chain(file_list1, file_list2)
        elif query == 'date':
            file_list1 = SharedFiles.objects.all().order_by('filename__date')
            file_list2 = SharedPrivateFiles.objects.all().order_by('filename__date')
            file_list = chain(file_list1, file_list2)
        elif query == 'ascending':
            file_list1 = SharedFiles.objects.all().order_by('filename__filename')
            file_list2 = SharedPrivateFiles.objects.all().order_by('filename__filename')
            file_list = chain(file_list1, file_list2)
        elif query == 'descending':
            file_list1 = SharedFiles.objects.all().order_by('-filename__filename')
            file_list2 = SharedPrivateFiles.objects.all().order_by('-filename__filename')
            file_list = chain(file_list1, file_list2)
        else:
            file_list1 = SharedFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
            file_list2 = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
            file_list = chain(file_list1, file_list2)
        context = {'file_list': file_list}
        return render(request, 'filesystem/sort_shared_file_grid.html' , context)

# function to search for specific folder in shared folders using filename as query
def shared_folder_search_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list1 = SharedFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
        folder_list2 = SharedPrivateFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
        folder_list = chain(folder_list1, folder_list2)
        context = {'folder_list': folder_list, 'folder_list1': folder_list1, 'folder_list2': folder_list2}
        return render(request, 'filesystem/search_shared_folder_list.html' , context)

# function to search for specific folder in shared folders using filename as query(GRID VIEW)
def shared_folder_search_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list1 = SharedFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
        folder_list2 = SharedPrivateFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
        folder_list = chain(folder_list1, folder_list2)
        context = {'folder_list': folder_list, 'folder_list1': folder_list1, 'folder_list2': folder_list2}
        return render(request, 'filesystem/search_shared_folder_grid.html' , context)

# function to sort shared folder by name and date created (GRID VIEW)
def sort_shared_folder_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'date':
            folder_list1 = SharedFolders.objects.all().order_by('folder_name__date')
            folder_list2 = SharedPrivateFolders.objects.all().order_by('folder_name__date')
            folder_list = chain(folder_list1, folder_list2)
        elif query == 'ascending':
            folder_list1 = SharedFolders.objects.all().order_by('folder_name__folder_name')
            folder_list2 = SharedPrivateFolders.objects.all().order_by('folder_name__folder_name')
            folder_list = chain(folder_list1, folder_list2)
            # sorted(folder_list)
        else:
            folder_list1 = SharedFolders.objects.all().order_by('-folder_name__folder_name')
            folder_list2 = SharedPrivateFolders.objects.all().order_by('-folder_name__folder_name')
            folder_list = chain(folder_list1, folder_list2)
        context = {'folder_list': folder_list, 'folder_list1': folder_list1, 'folder_list2': folder_list2}
        return render(request, 'filesystem/sort_shared_folder_grid.html' , context)

# function to display all recycled files 
def recycled_files_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        file_list = PublicFiles.objects.all()
        private_file_list = PrivateFiles.objects.all()
        context = {'file_list': file_list, 'private_file_list': private_file_list}
        return render(request, 'filesystem/recycled_files.html' , context)

# function to restore a file that has previously been recycled
def restore_file_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        try:
             file_instance = PublicFiles.objects.get(id=file_id)
        except:
             file_instance = PrivateFiles.objects.get(id=file_id)
        file_instance.recycled = False
        file_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)

# function to permanently delete recycled files   
def delete_file_view(request):
    if is_ajax(request=request) and request.method=='POST':
        file_id = request.POST.get('file_id')
        try:
             file_instance = PublicFiles.objects.get(id=file_id)
        except:
             file_instance = PrivateFiles.objects.get(id=file_id)
        file_instance.delete()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)

# function to display all recycled folders   
def recycled_folders_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder_list = PublicFolders.objects.all()
        private_folder_list = PrivateFolders.objects.all()
        context = {'folder_list': folder_list, 'private_folder_list': private_folder_list}
        return render(request, 'filesystem/recycled_folders.html' , context)

# function to restore recycled folders
def restore_folder_view(request):
    if is_ajax(request=request) and request.method=='POST':
        folder_id = request.POST.get('file_id')
        try:
             folder_instance = PublicFolders.objects.get(id=folder_id)
        except:
             folder_instance = PrivateFolders.objects.get(id=folder_id)
        folder_instance.recycled = False
        folder_instance.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)

# function to permanently delete folders    
def delete_folder_view(request):
    if is_ajax(request=request) and request.method=='POST':
        folder_id = request.POST.get('file_id')
        try:
             folder_instance = PublicFolders.objects.get(id=folder_id)
        except:
             folder_instance = PrivateFolders.objects.get(id=folder_id)
        folder_instance.delete()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)

# PRIVATE FILES/FOLDERS SECTION


# function to create private folder for multiple files/directory uploads
def create_private_folder_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.POST.get('createFolder')
        folder = PrivateFolders(folder_name=query, owner=request.user)
        folder.save()
        return redirect('private_folder_detail', folder.id) 

    
# function to search for specific private file using filename as query
def private_file_search_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFilesSearch')
        file_list = PrivateFiles.objects.filter(Q(filename__icontains=query))
        context = {'file_list': file_list}
        return render(request, 'filesystem/private_search_file_list.html' , context)
    
# function to sort private file by file type i.e pdf, docx, xlsx etc
def private_sort_file_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
            file_list = PrivateFiles.objects.filter(Q(filename__icontains=query))
        elif query == 'photos':
            file_list = PrivateFiles.objects.filter(Q(filename__icontains='jpg') | Q(filename__icontains='png') | Q(filename__icontains='jpeg'))
        else:
            file_list = PrivateFiles.objects.filter(Q(filename__icontains='mpeg') | Q(filename__icontains='mp4') | Q(filename__icontains='mkv') | Q(filename__icontains='mov'))
        print(file_list)
        context = {'file_list': file_list}
        return render(request, 'filesystem/private_sort_file_list.html' , context)

# function to search for specific private file using filename as query(GRID VIEW)
def private_file_search_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFilesSearch')
        file_list = PrivateFiles.objects.filter(Q(filename__icontains=query))
        context = {'file_list': file_list}
        return render(request, 'filesystem/private_search_file_grid.html' , context)

# function to sort private file by file type i.e pdf, docx, xlsx etc (GRID VIEW)
def sort_private_file_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
            file_list = PrivateFiles.objects.filter(Q(filename__icontains=query))
        elif query == 'photos':
            file_list = PrivateFiles.objects.filter(Q(filename__icontains='jpg') | Q(filename__icontains='png') | Q(filename__icontains='jpeg'))
        elif query == 'date':
            file_list = PrivateFiles.objects.all().order_by('date')
        elif query == 'ascending':
            file_list = PrivateFiles.objects.all().order_by('filename')
        elif query == 'descending':
            file_list = PrivateFiles.objects.all().order_by('-filename')
        else:
            file_list = PrivateFiles.objects.filter(Q(filename__icontains='mpeg') | Q(filename__icontains='mp4') | Q(filename__icontains='mkv') | Q(filename__icontains='mov'))
        context = {'file_list': file_list}
        return render(request, 'filesystem/private_sort_file_grid.html' , context)

# function to upload multiple private files to a folder
def multiple_private_file_upload_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        form = PrivateFilesMultipleCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PrivateFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('private_folder_detail', folder.id)
        else:
            form = PrivateFilesMultipleCreateForm()
        return redirect('private_folder_detail', folder.id)

# function to upload contents of a directory on local machine to private folder on digital library
def private_directory_upload_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        form = PrivateFolderCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PrivateFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('private_folder_detail', folder.id)
        else:
            form = PrivateFolderCreateForm()
        return redirect('private_folder_detail', folder.id)

    
# function to search for specific private folder using folder_name as query
def private_folder_search_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list = PrivateFolders.objects.filter(Q(folder_name__icontains=query))
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/private_search_folder_list.html' , context)
    

# function to display files within specific private folder
def private_folder_detail_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        try:
            shared_folder = SharedPrivateFolders.objects.get(Q(folder_name=folder) & Q(user=request.user))
        except:
            shared_folder = None
        associated_files = PrivateFiles.objects.filter(folder=folder)
        form1 = PrivateFilesMultipleCreateForm(initial={'owner': request.user})
        form2 = PrivateFolderCreateForm(initial={'owner': request.user})
        context = {'file_list': associated_files, 'form1': form1, 'form2': form2, 'folder': folder, 'shared_folder': shared_folder}
        return render(request, 'filesystem/private_folder_detail.html' , context)

# function to upload multiple private files to specific folder(GRID VIEW)
def multiple_private_file_upload_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        form = PrivateFilesMultipleCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PrivateFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('private_folder_detail_grid', folder.id)
        else:
            form = PrivateFilesMultipleCreateForm()
        return redirect('private_folder_detail_grid', folder.id)

# function to upload directory contents to specific private folder in digital library(GRID VIEW)
def private_directory_upload_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        form = PrivateFolderCreateForm(request.POST, request.FILES)
        files = request.FILES.getlist('filename')
        if form.is_valid():
            for f in files:
                new_file = PrivateFiles(filename=f, owner=request.user, folder=folder)
                new_file.save()
            return redirect('private_folder_detail_grid', folder.id)
        else:
            form = PrivateFolderCreateForm()
        return redirect('private_folder_detail_grid', folder.id)

# function to search for specific private folder using folder_name as query(GRID VIEW)
def private_folder_search_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('publicFoldersSearch')
        folder_list = PrivateFolders.objects.filter(Q(folder_name__icontains=query))
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/private_search_folder_grid.html' , context)

# function to sort private folder by name and date created (GRID VIEW)
def sort_private_folder_grid_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        query = request.GET.get('sortInput')
        if query == 'date':
            folder_list = PrivateFolders.objects.all().order_by('date')
        elif query == 'ascending':
            folder_list = PrivateFolders.objects.all().order_by('folder_name')
        else:
            folder_list = PrivateFolders.objects.all().order_by('-folder_name')
        context = {'folder_list': folder_list}
        return render(request, 'filesystem/private_sort_folder_grid.html' , context)

# function to list files within specific private folders (GRID VIEW)
def private_folder_detail_grid_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        folder = PrivateFolders.objects.get(id=pk)
        try:
            shared_folder = SharedPrivateFolders.objects.get(Q(folder_name=folder) & Q(user=request.user))
        except:
            shared_folder = None
        associated_files = PrivateFiles.objects.filter(folder=folder)
        form1 = PrivateFilesMultipleCreateForm(initial={'owner': request.user})
        form2 = PrivateFolderCreateForm(initial={'owner': request.user})
        context = {'file_list': associated_files, 'form1': form1, 'form2': form2, 'folder': folder, 'shared_folder': shared_folder}
        return render(request, 'filesystem/private_folder_detail_grid.html' , context)


# function to show space usage on digital library
def show_statistics_view(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    elif not (request.user.is_custom_admin):
        return render(request, template_name='filesystem/file_list.html', status=404)
    else:
        pubfilesize = 0
        privfilesize = 0
        pubfolsize = 0
        privfolsize = 0
        usersize = 0
        publicfiles = PublicFiles.objects.filter(folder__isnull=True)
        privatefiles = PrivateFiles.objects.filter(folder__isnull=True)
        publicfolders = PublicFiles.objects.filter(folder__isnull=False)
        privatefolders = PrivateFiles.objects.filter(folder__isnull=False)

        users = get_user_model().objects.all()
        for u in users:
            if u.profile_picture:
                usersize = usersize + u.profile_picture.size
        
        for f in publicfiles:
            pubfilesize = pubfilesize + f.filename.size


        for pf in privatefiles:
            privfilesize = privfilesize + pf.filename.size

        for fol in publicfolders:
            pubfolsize = pubfolsize + fol.filename.size
    
        for pfol in privatefolders:
            privfolsize = privfolsize + pfol.filename.size
        
        totalfilesize = pubfilesize + privfilesize
        totalfolsize  = pubfolsize + privfolsize
        totalfilesize = round(totalfilesize/1000000000, 1) 
        totalfolsize = round(totalfolsize/1000000000, 1) 
        usersize = round(usersize/1000000000, 0)
        offset = (200 - totalfolsize - totalfilesize - usersize)
        usedspace = totalfilesize + totalfolsize + usersize
        availablespace = usedspace + offset

        projects_data = [
            {
                'Parameter': 'Files',
                'Value': totalfilesize,
            },
            {
                'Parameter': 'Folders',
                'Value': totalfolsize,
            },
            {
                'Parameter': 'Users',
                'Value': usersize,
            },
            {
                'Parameter': '',
                'Value': offset,
            },
        ]
        df = pd.DataFrame(projects_data)
        df2 = df.set_index("Parameter").unstack().to_frame().reset_index()
        fig = px.bar(
            df2,
            y="level_0",
            x=0,
            color="Parameter",
            color_discrete_map={
                "Files": "#195F89",
                "Folders": "#1D88CB",
                "Users": "#067AC1",
                "": "#F5FAFC",
            },
            width=1200,
            height=250, 
            text="Parameter",
            title = f"{usedspace}GB of {availablespace}GB used",
        )
        fig.update_layout(
            yaxis={'visible': False, 'showticklabels': False},
            xaxis={'visible': False, 'showticklabels': False},
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(texttemplate="%{text}<br>%{x}GB", hovertemplate=".")
        stacked_bar = plot(fig, output_type="div")
        context = {'plot_div': stacked_bar, 'availablespace': availablespace, 'usedspace': usedspace}
        return render(request, 'filesystem/project_data.html', context)


# # function to search for specific file in shared private files using filename as query
# def shared_private_file_search_view(request):
#         query = request.GET.get('publicFilesSearch')
#         file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
#         context = {'file_list': file_list}
#         return render(request, 'filesystem/private_search_shared_file_list.html' , context)

# # function to sort file in shared private files by file type i.e pdf, docx, xlsx etc
# def sort_shared_private_file_view(request):
#         query = request.GET.get('sortInput')
#         if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
#         elif query == 'photos':
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
#         else:
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
#         context = {'file_list': file_list}
#         return render(request, 'filesystem/private_sort_shared_file_list.html' , context)

# # function to search for specific file in shared files using filename as query(GRID VIEW)
# def shared_private_file_search_grid_view(request):
#         query = request.GET.get('publicFilesSearch')
#         file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
#         context = {'file_list': file_list}
#         return render(request, 'filesystem/private_search_shared_file_grid.html' , context)

# # function to sort file in shared files by file type i.e pdf, docx, xlsx etc(GRID VIEW)
# def sort_shared_private_file_grid_view(request):
#         query = request.GET.get('sortInput')
#         if query == 'pdf' or query == 'docx' or query == 'xlsx' or query == 'pptx':
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains=query))
#         elif query == 'photos':
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='jpg') | Q(filename__filename__icontains='png') | Q(filename__filename__icontains='jpeg'))
#         elif query == 'date':
#             file_list = SharedPrivateFiles.objects.all().order_by('filename__date')
#         elif query == 'ascending':
#             file_list = SharedPrivateFiles.objects.all().order_by('filename__filename')
#         elif query == 'descending':
#             file_list = SharedPrivateFiles.objects.all().order_by('-filename__filename')
#         else:
#             file_list = SharedPrivateFiles.objects.filter(Q(filename__filename__icontains='mpeg') | Q(filename__filename__icontains='mp4') | Q(filename__filename__icontains='mkv') | Q(filename__filename__icontains='mov'))
#         context = {'file_list': file_list}
#         return render(request, 'filesystem/private_sort_shared_file_grid.html' , context)

# # function to search for specific private folder in shared folders using filename as query
# def shared_private_folder_search_view(request):
#         query = request.GET.get('publicFoldersSearch')
#         folder_list = SharedPrivateFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
#         context = {'folder_list': folder_list}
#         return render(request, 'filesystem/private_search_shared_folder_list.html' , context)

# # function to search for specific private folder in shared folders using filename as query(GRID VIEW)
# def shared_private_folder_search_grid_view(request):
#         query = request.GET.get('publicFoldersSearch')
#         folder_list = SharedPrivateFolders.objects.filter(Q(folder_name__folder_name__icontains=query))
#         context = {'folder_list': folder_list}
#         return render(request, 'filesystem/private_search_shared_folder_grid.html' , context)

# # function to sort shared private folder by name and date created (GRID VIEW)
# def sort_shared_private_folder_grid_view(request):
#         query = request.GET.get('sortInput')
#         if query == 'date':
#             folder_list = SharedPrivateFolders.objects.all().order_by('folder_name__date')
#         elif query == 'ascending':
#             folder_list = SharedPrivateFolders.objects.all().order_by('folder_name__folder_name')
#         else:
#             folder_list = SharedPrivateFolders.objects.all().order_by('-folder_name__folder_name')
#         context = {'folder_list': folder_list}
#         return render(request, 'filesystem/private_sort_shared_folder_grid.html' , context)









# #CBV to get public file list for get request and add new files to public files model on post request
# class PublicFileCreateView(CreateView):
#     model = PublicFiles
#     form_class = PublicFilesCreateForm
#     template_name = 'filesystem/file_list.html'
        
#     def post(self, request, *args, **kwargs):
#             form = self.form_class(self.request.POST, self.request.FILES)
#             files = request.FILES.getlist('filename')
#             if form.is_valid():
#                 for f in files:
#                     new_file = self.model(filename=f, owner=self.request.user)
#                     new_file.save()
#                 return redirect('file_list')
#             else:
#                 form = self.form_class()
#             return redirect('file_list')

#     def get(self, request, *args, **kwargs):
#         url_parameter = self.request.GET.get("q")
#         if url_parameter:
#             users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
#         else:
#             users = None
#         file_list = PublicFiles.objects.all()
#         shared_list = SharedFiles.objects.all()
#         form = self.form_class(initial={'owner': self.request.user})
#         context = { 'file_list':file_list, 'users': users, 'shared_list': shared_list, 'form': form}
#         does_req_accept_json = request.accepts("application/json")
#         is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
#         if is_ajax_request:
#             html = render_to_string(
#                 template_name="filesystem/file_list_result_partial.html", 
#                 context={ 'users': users}
#             )
#             data_dict = {"html_from_view": html}
#             return JsonResponse(data=data_dict, safe=False)
#         return render(request, self.template_name , context)



#CBV to get public file list for get request and add new files to public files model on post request
class PublicFileCreateView(CreateView):
    model = PublicFiles
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/file_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list')
            else:
                form = self.form_class()
            return redirect('file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        file_id = self.request.GET.get("file_id")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = PublicFiles.objects.all()
        shared_list = SharedFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'users': users, 'shared_list': shared_list, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users,}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    


    
#CBV to get public file list for get request and add new files to public files model on post request(GRID VIEW)
class PublicFileCreateGridView(CreateView):
    model = PublicFiles
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/file_list_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list_grid')
            else:
                form = self.form_class()
            return redirect('file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = PublicFiles.objects.all()
        shared_list = SharedFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'users': users, 'shared_list': shared_list, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    

    
# CBV to update public files 
class PublicFileUpdateView(UpdateView):
    model = PublicFiles
    form_class = PublicFilesUpdateForm
    template_name = 'filesystem/file_update.html'
    context_object_name = 'file'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)

    def model_form_upload(request):
        if request.method == 'POST':
            form = PublicFilesUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('file_list')
        else:
            form =PublicFilesUpdateForm()
        return render(request, 'update_public_file', {
            'form': form
        })
    

    
#CBV to get public folder list for get request and add new files to public files model on post request
class PublicFolderCreateView(CreateView):
    model = PublicFolders
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/folder_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PublicFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list')
            else:
                form = self.form_class()
            return redirect('file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = PublicFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    


    

#CBV to get public folder list for get request and add new files to public files model on post request(grid pattern)
class PublicFolderCreateGridView(CreateView):
    model = PublicFolders
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/folder_list_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PublicFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list_grid')
            else:
                form = self.form_class()
            return redirect('file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = PublicFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    



#CBV to get shared file list for get request and add new files to public files model on post request
class SharedFileCreateView(CreateView):
    model = PublicFiles
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/file_shared.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list')
            else:
                form = self.form_class()
            return redirect('file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = SharedFiles.objects.all()
        private_file_list = SharedPrivateFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'private_file_list':private_file_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    




#CBV to get shared file list for get request and add new files to public files model on post request(grid pattern)
class SharedFileCreateGridView(CreateView):
    model = PublicFiles
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/file_shared_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list_grid')
            else:
                form = self.form_class()
            return redirect('file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = SharedFiles.objects.all()
        private_file_list = SharedPrivateFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'private_file_list':private_file_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    


   
#CBV to get shared folder list for get request and add new files to public files model on post request
class SharedFolderCreateView(CreateView):
    model = PublicFolders
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/folder_shared.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PublicFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list')
            else:
                form = self.form_class()
            return redirect('file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = SharedFolders.objects.all()
        private_folder_list = SharedPrivateFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'private_folder_list': private_folder_list ,'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    


        
#CBV to get shared folder list for get request and add new files to public files model on post request(grid pattern)
class SharedFolderCreateGridView(CreateView):
    model = PublicFolders
    form_class = PublicFilesCreateForm
    template_name = 'filesystem/folder_shared_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PublicFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('file_list_grid')
            else:
                form = self.form_class()
            return redirect('file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = SharedFolders.objects.all()
        private_folder_list = SharedPrivateFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'private_folder_list': private_folder_list ,'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
        








#CBV to get private file list for get request and add new files to private files model on post request
class PrivateFileCreateView(CreateView):
    model = PrivateFiles
    form_class = PrivateFilesCreateForm
    template_name = 'filesystem/private_file_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('private_file_list')
            else:
                form = self.form_class()
            return redirect('private_file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = PrivateFiles.objects.all()
        shared_list = SharedPrivateFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'users': users, 'shared_list': shared_list, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    
#CBV to get private file list for get request and add new files to private files model on post request(GRID VIEW)
class PrivateFileCreateGridView(CreateView):
    model = PrivateFiles
    form_class = PrivateFilesCreateForm
    template_name = 'filesystem/private_file_list_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = self.model(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('private_file_list_grid')
            else:
                form = self.form_class()
            return redirect('private_file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        file_list = PrivateFiles.objects.all()
        shared_list = SharedPrivateFiles.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'file_list':file_list, 'users': users, 'shared_list': shared_list, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    
# CBV to update private files 
class PrivateFileUpdateView(UpdateView):
    model = PrivateFiles
    form_class = PrivateFilesUpdateForm
    template_name = 'filesystem/private_file_update.html'
    context_object_name = 'file'
    

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)

    def model_form_upload(self,request, *args, **kwargs):
        if request.method == 'POST':
            form = PrivateFilesUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('private_file_list')
        else:
            form =PrivateFilesUpdateForm()
        return render(request, 'update_private_file', {
            'form': form
        })
    
#CBV to get private folder list for get request and add new files to private files model on post request
class PrivateFolderCreateView(CreateView):
    model = PrivateFolders
    form_class = PrivateFilesCreateForm
    template_name = 'filesystem/private_folder_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PrivateFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('private_file_list')
            else:
                form = self.form_class()
            return redirect('private_file_list')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = PrivateFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    
#CBV to get private folder list for get request and add new files to private files model on post request(grid pattern)
class PrivateFolderCreateGridView(CreateView):
    model = PrivateFolders
    form_class = PrivateFilesCreateForm
    template_name = 'filesystem/private_folder_list_grid.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST, self.request.FILES)
            files = request.FILES.getlist('filename')
            if form.is_valid():
                for f in files:
                    new_file = PrivateFiles(filename=f, owner=self.request.user)
                    new_file.save()
                return redirect('private_file_list_grid')
            else:
                form = self.form_class()
            return redirect('private_file_list_grid')

    def get(self, request, *args, **kwargs):
        url_parameter = self.request.GET.get("q")
        if url_parameter:
            users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
        else:
            users = None
        folder_list = PrivateFolders.objects.all()
        form = self.form_class(initial={'owner': self.request.user})
        context = { 'folder_list':folder_list, 'users': users, 'form': form}
        does_req_accept_json = request.accepts("application/json")
        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
        if is_ajax_request:
            html = render_to_string(
                template_name="filesystem/file_list_result_partial.html", 
                context={ 'users': users}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
        return render(request, self.template_name , context)
    

#CBV to get announcement form and post announcement to database 
class AnnouncementCreateView(CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcement/create_announcement.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
            form = self.form_class(self.request.POST)
            users = get_user_model().objects.all()
            admins = get_user_model().objects.filter(is_custom_admin=True)
            if form.is_valid():
                new_announcement = form.save()
                if new_announcement.send_to == 'Everyone':
                    for user in users:
                        Notification.objects.create(notification_type=5, to_user=user, from_user=request.user, announcement=new_announcement)
                else:
                    for admin in admins:
                        Notification.objects.create(notification_type=6, to_user=admin, from_user=request.user, announcement=new_announcement)
                return redirect('announcement')
            else:
                form = self.form_class()
            return redirect('announcement')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name , context)

    
# #CBV to get shared private file list for get request and add new files to private files model on post request
# class SharedPrivateFileCreateView(CreateView):
#     model = PrivateFiles
#     form_class = PrivateFilesCreateForm
#     template_name = 'filesystem/private_file_shared.html'
        
#     def post(self, request, *args, **kwargs):
#             form = self.form_class(self.request.POST, self.request.FILES)
#             files = request.FILES.getlist('filename')
#             if form.is_valid():
#                 for f in files:
#                     new_file = self.model(filename=f, owner=self.request.user)
#                     new_file.save()
#                 return redirect('file_list')
#             else:
#                 form = self.form_class()
#             return redirect('file_list')

#     def get(self, request, *args, **kwargs):
#         url_parameter = self.request.GET.get("q")
#         if url_parameter:
#             users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
#         else:
#             users = None
#         file_list = SharedPrivateFiles.objects.all()
        
#         form = self.form_class(initial={'owner': self.request.user})
#         context = { 'file_list':file_list, 'users': users, 'form': form}
#         does_req_accept_json = request.accepts("application/json")
#         is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
#         if is_ajax_request:
#             html = render_to_string(
#                 template_name="filesystem/file_list_result_partial.html", 
#                 context={ 'users': users}
#             )
#             data_dict = {"html_from_view": html}
#             return JsonResponse(data=data_dict, safe=False)
#         return render(request, self.template_name , context)
    
# #CBV to get shared private file list for get request and add new files to private files model on post request(grid pattern)
# class SharedPrivateFileCreateGridView(CreateView):
#     model = PrivateFiles
#     form_class = PrivateFilesCreateForm
#     template_name = 'filesystem/private_file_shared_grid.html'
        
#     def post(self, request, *args, **kwargs):
#             form = self.form_class(self.request.POST, self.request.FILES)
#             files = request.FILES.getlist('filename')
#             if form.is_valid():
#                 for f in files:
#                     new_file = self.model(filename=f, owner=self.request.user)
#                     new_file.save()
#                 return redirect('private_file_list_grid')
#             else:
#                 form = self.form_class()
#             return redirect('private_file_list_grid')

#     def get(self, request, *args, **kwargs):
#         url_parameter = self.request.GET.get("q")
#         if url_parameter:
#             users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
#         else:
#             users = None
#         file_list = SharedPrivateFiles.objects.all()
#         form = self.form_class(initial={'owner': self.request.user})
#         context = { 'file_list':file_list, 'users': users, 'form': form}
#         does_req_accept_json = request.accepts("application/json")
#         is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
#         if is_ajax_request:
#             html = render_to_string(
#                 template_name="filesystem/file_list_result_partial.html", 
#                 context={ 'users': users}
#             )
#             data_dict = {"html_from_view": html}
#             return JsonResponse(data=data_dict, safe=False)
#         return render(request, self.template_name , context)
    
# #CBV to get shared private folder list for get request and add new files to private files model on post request
# class SharedPrivateFolderCreateView(CreateView):
#     model = PrivateFolders
#     form_class = PrivateFilesCreateForm
#     template_name = 'filesystem/private_folder_shared.html'
        
#     def post(self, request, *args, **kwargs):
#             form = self.form_class(self.request.POST, self.request.FILES)
#             files = request.FILES.getlist('filename')
#             if form.is_valid():
#                 for f in files:
#                     new_file = PrivateFiles(filename=f, owner=self.request.user)
#                     new_file.save()
#                 return redirect('private_file_list')
#             else:
#                 form = self.form_class()
#             return redirect('private_file_list')

#     def get(self, request, *args, **kwargs):
#         url_parameter = self.request.GET.get("q")
#         if url_parameter:
#             users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
#         else:
#             users = None
#         folder_list = SharedPrivateFolders.objects.all()
#         print(folder_list)
#         form = self.form_class(initial={'owner': self.request.user})
#         context = { 'folder_list':folder_list, 'users': users, 'form': form}
#         does_req_accept_json = request.accepts("application/json")
#         is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
#         if is_ajax_request:
#             html = render_to_string(
#                 template_name="filesystem/file_list_result_partial.html", 
#                 context={ 'users': users}
#             )
#             data_dict = {"html_from_view": html}
#             return JsonResponse(data=data_dict, safe=False)
#         return render(request, self.template_name , context)
    
# #CBV to get shared folder list for get request and add new files to private files model on post request(grid pattern)
# class SharedPrivateFolderCreateGridView(CreateView):
#     model = PrivateFolders
#     form_class = PrivateFilesCreateForm
#     template_name = 'filesystem/private_folder_shared_grid.html'
        
#     def post(self, request, *args, **kwargs):
#             form = self.form_class(self.request.POST, self.request.FILES)
#             files = request.FILES.getlist('filename')
#             if form.is_valid():
#                 for f in files:
#                     new_file = PrivateFiles(filename=f, owner=self.request.user)
#                     new_file.save()
#                 return redirect('file_list_grid')
#             else:
#                 form = self.form_class()
#             return redirect('file_list_grid')

#     def get(self, request, *args, **kwargs):
#         url_parameter = self.request.GET.get("q")
#         if url_parameter:
#             users = get_user_model().objects.filter(Q(username__icontains=url_parameter) | Q(first_name__icontains=url_parameter) | Q(last_name__icontains=url_parameter))
#         else:
#             users = None
#         folder_list = SharedPrivateFolders.objects.all()
#         form = self.form_class(initial={'owner': self.request.user})
#         context = { 'folder_list':folder_list, 'users': users, 'form': form}
#         does_req_accept_json = request.accepts("application/json")
#         is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
#         if is_ajax_request:
#             html = render_to_string(
#                 template_name="filesystem/file_list_result_partial.html", 
#                 context={ 'users': users}
#             )
#             data_dict = {"html_from_view": html}
#             return JsonResponse(data=data_dict, safe=False)
#         return render(request, self.template_name , context)
