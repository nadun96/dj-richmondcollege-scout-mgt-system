import time
from django.contrib.auth import get_user_model
User = get_user_model()


def generate_username():
    """ generate username """
    current_year = time.strftime("%Y")
    # this year joined count
    count = User.objects.filter(date_joined__year=current_year).count()
    # base username
    base_username = f'SC/{current_year}/{count+1}'
    # Check if the base username already exists
    if User.objects.filter(username=base_username).exists():
        # If the base username already exists, add a suffix to make it unique
        suffix = 1
        while True:
            # Generate a new username with the suffix
            new_username = f'{base_username}_{suffix}'

            # Check if the new username is unique
            if not User.objects.filter(username=new_username).exists():
                # If the new username is unique, return it
                return new_username

            # If the new username is not unique, increment the suffix and try again
            suffix += 1
    else:
        # If the base username is unique, return it
        return base_username


""" old way """
# generate student number as example
# max_id = User.objects.aggregate(id=Max('id'))
# max_id = int(max_id['id']) + 1
# currentYear = time. strftime("%Y")
# username = f'SC/{currentYear}/{str(max_id)}'
