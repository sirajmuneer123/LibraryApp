from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=128)
    book_code = models.CharField(max_length=36, unique=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.title


class Order(models.Model):
    order_status = (
        ('1', 'placed'),
        ('2', 'returned'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=order_status)


    class Meta:
        default_permissions = ()


    def __str__(self):
        return self.customer.first_name


class TimePeriod(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        default_permissions = ()
    

    def __str__(self):
        return str(self.start_time)



class UserPermissions(models.Model):
    """
    user permission model
    """
    name = models.CharField(max_length=100, default="UserPermissions")

    class Meta:
        default_permissions = ()
        permissions = (
                ('staff_add_book', 'Add Book'),
                )

        def __str__(self):
            return self.name