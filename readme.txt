To run code from this repository
1. Install Docker and run
    Use this link on mac - https://docs.docker.com/desktop/install/mac-install/
    Use this link on windows - https://docs.docker.com/desktop/install/windows-install/

2. Build docker image - docker-compose build 

3. Make migrations and migrate database -  
    docker-compose run --rm app sh -c "python manage.py makemigrations"
    docker-compose run --rm app sh -c "python manage.py migrate"

4. Create super user 
    docker-compose run --rm app sh -c "python manage.py createsuperuser"

5. Set superuser account to active from django shell 
    docker-compose run --rm app sh -c "python manage.py shell"
    from users.models import CustomUser
    my_user = CustomUser.objects.get(username='append_your_super_user_name_to_this_query')
    my_user.active = True
    my_user.save()
    exit()

6. Set "is_custom_admin" status of superuser to "True" and login with superuser. The configuration side
    of the app is hidden from other user roles asides admin.
    docker-compose run --rm app sh -c "python manage.py shell"
    from users.models import CustomUser
    my_user = CustomUser.objects.get(username='append_your_super_user_name_to_this_query')
    my_user.is_custom_admin = True
    my_user.save()
    exit()

7. Start up local server - docker-compose up

8. Use super user to subsequently set registered accounts to active from django admin panel
    127.0.0.1/admin


9. Use the links in the "Configuration" dropdown to navigate the admin side of the app. On the various 
    pages of the admin side the red colored link usually embeds an action.

10. To get the user update page(this page is equivalent to page21 on the mockup), click on the user image or 
arrow facing down on the top right corner of navbar.

11. url routes 
    signup - 127.0.0.1:8000/accounts/signup
    login - 127.0.0.1:8000/accounts/login
    logout - 127.0.0.1:8000/accounts/logout
    password change - 127.0.0.1:8000/accounts/password/change
    inactive account - 127.0.0.1:8000/accounts/inactive
    confirm email - 127.0.0.1:8000/accounts/confirm-email
    password reset - 127.0.0.1:8000/accounts/password/reset
    user list - 127.0.0.1:8000/accounts/profile

12. Be sure to rebuild docker image with instructions from 2(note that base python image on Dockerfile has 
been changed from alpine version to regular version to facilitate some third party packages), migrate all 
apps with instructions from 3, create and set up super user with instructions from 4 - 8. Login and enjoy!
    