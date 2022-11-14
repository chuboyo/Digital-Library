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
    my_user = CustomUser.objects.get(username=append_your_super_user_name_to_this_query)
    my_user.active = True
    my_user.save()
    exit()

6. Start up local server - docker-compose up

7. Use super user to subsequently set registered accounts to active from django admin panel
    127.0.0.1/admin



8. url routes 
    signup - 127.0.0.1:8000/accounts/signup
    login - 127.0.0.1:8000/accounts/login
    logout - 127.0.0.1:8000/accounts/logout
    password change - 127.0.0.1:8000/accounts/password/change
    inactive account - 127.0.0.1:8000/accounts/inactive
    confirm email - 127.0.0.1:8000/accounts/confirm-email
    password reset - 127.0.0.1:8000/accounts/password/reset
    user list - 127.0.0.1:8000/accounts/profile
    