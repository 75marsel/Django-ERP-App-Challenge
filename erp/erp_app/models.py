from django.db import models
from django.db.models import Sum, Q, F, QuerySet
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
    )
# implement a uuid for 
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
import uuid


class Tenant(models.Model):
    # id can be a uuid, but for this we can implement a simpler approach
    # that is supported by wide databases
    id = models.AutoField(primary_key=True, editable=False)
    
    """
    Name validator using RegexValidator
    https://docs.djangoproject.com/en/5.1/ref/validators/#django.core.validators.RegexValidator
    
    
    name: Name of the tenant (string).
    """
    
    # adjust the max length of name as needed
    # different countries may have multiple characters or require more for a full name
    NAME_MAX_LENGTH = 60
    
    name_validator = RegexValidator(
        regex = r"^[a-zA-z\s]*$",
        message="Alphabet characters and spaces are only allowed.",
    )
    
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[name_validator],
        # unique=True, # in some countries people have same names
    )
    
    """
    Lease Date Time
    using Aware datetime objects
    https://docs.djangoproject.com/en/5.1/topics/i18n/timezones/
    
    lease_start: Lease start date (datetime).
    lease_end: Lease end date (datetime).
    """
    
    lease_start = models.DateTimeField(
        # auto_now_add=True,
        # default=timezone.now
    )
    lease_end = models.DateTimeField()
    
    # filler variable for rent due
    # this can have a small pay button to increase by 1 month
    next_payment_due = models.DateTimeField(
        blank=True,
        null=True,
    )
    
    """
    max_digits: 14 (billion)
    monthly_rent: Monthly rent paid by the tenant (float).
    """
    
    monthly_rent = models.DecimalField(
        max_digits=14, # 000,000,000,000.00
        decimal_places=2
    )
    
    """
    Unit Number can be the following for example:
    
    101, 4A, A-01 etc..
    it can be a possible design to exclude "Room" in "Room A-35"
    
    The variable can be added manually


    unit: The unit number occupied by the tenant (string).
    """
    unit = models.CharField(max_length=10, unique=False, blank=False)
    
    def save(self, *args, **kwargs):
        if not self.next_payment_due:
            self.next_payment_due = self.lease_start + timedelta(days=31)
        super(Tenant, self).save(*args, **kwargs)
    
    def renew_lease(self, extended_date: datetime) -> None:
        extended_date = make_aware(extended_date)
        
        if self.lease_end < extended_date:
            self.lease_end = extended_date
            self.save()
        else:
            raise ValidationError("Extended date must be greater than the current lease end")
    
    def add_unit(self, unit) -> None:
        if unit and not self.unit:
            self.unit = unit
            self.save()
    
    def remove_unit(self) -> None:
        if not self.unit:
            raise ValidationError("Error removing unit!")
        self.unit = ""
        self.save()
    
    def __str__(self) -> str:
        return self.name
  
    
class Property(models.Model):
    """Property Model
    
    Attrs:
        id: Unique identifier for the property.
        address: Address of the property (string).
        property_type: Type of property (e.g., "residential", "commercial").
        units: Number of rentable units in the property (for multi-unit buildings).
        tenants: A list of Tenantobjects that are leasing the property.
    Methods:
        __init__: Initializes the property with given attributes.
        add_tenant: Adds a Tenant to the property, assigning them to a unit.
        remove_tenant: Removes a Tenant from the property.
        calculate_occupancy_rate: Calculates the current occupancy rate of the property.
        calculate_total_rent: Computes total rent collected from the tenants.
    """
    
    
    # id can be a uuid, but for this we can implement a simpler approach
    # that is supported by wide databases
    id = models.AutoField(primary_key=True, editable=False)
    # address of the property
    # the max length can be adjusted
    address = models.CharField(max_length=200, unique=True)
    
    """
    Model Field Reference Documentation:
    https://docs.djangoproject.com/en/5.1/ref/models/fields/
    
    property_type: Type of property (e.g., "residential", "commercial").
    
    """
    
    COMMERICIAL = "Commercial"
    PRIVATE = "Private"
    
    PROPERTY_TYPE_CHOICES = {
        COMMERICIAL: "Commericial",
        PRIVATE: "Private",
    }
    
    property_type = models.CharField(
        max_length=10,
        choices=PROPERTY_TYPE_CHOICES,
        default=PRIVATE,
    )
    
    """
    Value Validator
    https://docs.djangoproject.com/en/5.1/ref/validators/
    
    units: Number of rentable units in the property (for multi-unit buildings).
    
    Although, it does not mentioned the min-max untis, it is advisable to add one.
    """
    
    # minimum number of units accepted
    MINIMUM_UNITS = 1
    # maximum number of units accepted
    MAXIMUM_UNITS = 100
    
    units = models.IntegerField(validators=[
        MinValueValidator(MINIMUM_UNITS),
        MaxValueValidator(MAXIMUM_UNITS)
    ])
    
    current_units = models.IntegerField(validators=[
        MinValueValidator(MINIMUM_UNITS),
        MaxValueValidator(MAXIMUM_UNITS)
        ],
        default=0
    )
    
    """
    Tenants relationship
    
    https://docs.djangoproject.com/en/5.1/topics/db/examples/many_to_many/
    
    Tenants can have multiple property and a property can have multiple tenants
    """
    
    tenants = models.ManyToManyField(
        Tenant,
        blank=True,
        related_name='properties',
    )
    
    
    def add_tenant(self, tenant: Tenant, unit_room: "UnitRoom"):
        """
        Adds a tenant by providing the tenant object (current user
        and the preffered unit
        
        Args:
            tenant: Singel Model object
            preffered_unit: Single Model object <UnitRoom: DOG001>
        """
        
        # # check if the preferred unit is NOT available and valid
        # if preffered_unit < 1 or preffered_unit > self.units:
        #     raise ValidationError(f"Preferred Unit out of range!")

        # # check if the preferred unit is not available
        # if Tenant.objects.filter(property=self, unit=preffered_unit).exists():
        #     raise ValidationError(f"Preferred Unit out of range!")

        if not unit_room.tenant is None:
            raise ValidationError("Preferred Unit is Occupied!")
        
        if self.tenants.count() >= self.units:
            raise ValueError("All units are Occupied!")
        
        # # check if the tenant is in the property
        # if not self.tenants.filter(id=tenant.id).exists():
        #     raise ValidationError("Tenant not in a property!")
        
        # add tenant to the property
        self.tenants.add(tenant)
        
        # check if the preffered unit room is not empty then add it to the preffered unit
        if unit_room:
            # add the tenant to the Unit Room selected
            unit_room.tenant = tenant
            # save the specific fields: tenant
            # unit_room.save(update_fields=["tenant"])
            unit_room.save()
            # change the unit of tenant to the unit number of the unit room
            tenant.unit = unit_room.unit_number
            # save the specific fields: unit
            # tenant.save(update_fields=["unit"])
            tenant.save()
            self.current_units +=1 
            self.save()
        else:
            raise ValidationError("wRONG FIELDS!")
        print(self.current_units)
    
# Removes the passed tenant object from the tenants attribute and also removes the tenant's room
    def remove_tenant(self, tenant):
        if tenant and self.current_units > 0:
            # Remove the tenant from the tenants list
            self.tenants.remove(tenant)

            # Access and clear the tenant's unit room(s)
            # Assuming each tenant has one unit room, but adjust for multiple unit rooms if needed
            tenant_unit_rooms = tenant.tenant.all()  # Retrieves all unit rooms associated with the tenant
            print(f"tenant room: {tenant_unit_rooms}")
            for unit_room in tenant_unit_rooms:
                unit_room.tenant = None  # Remove the tenant from the unit room
                unit_room.save()  # Save the change to the database
            
            self.current_units -= 1
            self.save()  # Save changes to the property model
    
    # foreign key add
    def add_room(self, room):
        if self.unit_rooms.count() >= self.units:
            raise ValueError("Property units already full!")
        print(self.unit_rooms.count())
        room.property = self
        room.save()
    
    def remove_room(self, room):
        room.property = None
        room.save()
        
    
    # calculate the occupancy rate of the property

    def calculate_occupancy_rate(self) -> int:
        return round((self.tenants.count() / self.units) * 100, 2)
    
    # calculate the total rent of a property where tenant must have a unit room
    # documentation for complex queries: https://docs.djangoproject.com/en/5.1/topics/db/queries/#complex-lookups-with-q-objects

    def calculate_total_rent(self):
        total = self.tenants.filter(~Q(unit=None)).aggregate(
            total_units=Sum("monthly_rent")
        )["total_units"] or 0
        return total

    def get_number_of_vacant_units(self):
        # can add a filter to tenants to only who has unit rooms
        return self.units - self.tenants.count()
    
    def delete_property(self):
        if self.tenants.all():
            for t in self.tenants.all():
                t.unit = ""
                t.save()
        self.delete()
    
    def __str__(self) -> str:
        return self.address


class UnitRoom(models.Model):
    """A placeholder for UnitRoom or unit of Tenant Class Model

    Attrs:
        unit_number: the Unit Number (A-01)
        tenant: ForeignKey relationship with tenant (owner)
        proeprty: ForeignKey relationship with property (at what property does this room belong)
        
    Methods:
        __str__: dunder method that returns a string when the object is called without ()
        sort_search: Returns a QuerySet of Rooms sorted to the given Property
    """
    id = models.AutoField(primary_key=True, editable=False)
    
    # Unit Number for Tenant's unit attribute
    unit_number = models.CharField(max_length=10, unique=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        blank = True,
        null=True,
        related_name='tenant',
    )
    
    # Point where this unit room belongs
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='unit_rooms',
    )
    
    def __str__(self) -> str:
        return self.unit_number

    def add_property(self, property):
        self.property = property
        self.save()
    
    def remove_property(self):
        self.property = None
        self.remove_tenant()
        self.save()
        
    def add_tenant(self, tenant):
        self.tenant = tenant
        self.save()
    
    def remove_tenant(self):
        if self.tenant:
            self.tenant = None
            self.save()
    

class LeaseManager(models.Model):
    """A model that will be responsible for adding property to the portfolio

    Args:
        models (_type_): _description_
    """
    name = models.CharField(
        max_length=50,
        blank=False,
    )
    
    properties = models.ManyToManyField(
        Property,
        related_name='lease_manager',
    )
    
    # add property to the lease manager by passing a property model object
    
    def add_property(self, property):
        if property is None:
            raise ValidationError("Property not found!")
        self.properties.add(property)
            
    # remove property to the lease manager by passing a property model object
    
    def remove_property(self, property):
        if not property:
            raise ValidationError("Property not found!")
        self.properties.remove(property)    
    
    # returns all properties currently possesed by lease manager    
    
    def retrieve_all_property(self) -> QuerySet[Property]:
        return self.properties
    
    # find vacant units in every property of this lease manager
    
    def find_vacant_units(self) -> list[Property]:
        result = []
        for property in self.properties.filter(current_units__lt=F('units')):
            result.append(property)
        return result

    # generate a lease expiry report in between dates

    def generate_lease_expiry_report(self, start_lease_date, end_lease_date, properties):
        start_lease_date = make_aware(start_lease_date)
        end_lease_date = make_aware(end_lease_date)
        
        try:
            return Tenant.objects.filter(lease_end__range=(start_lease_date, end_lease_date),
                                         properties=properties,
                                         )
        except self.DoesNotExist:
            return None
    
    # calculate the total revenue of every property that the lease manager possess
    
    def calculate_total_revenue(self) -> int:
        total = 0
        for p in self.properties.all():
            total += p.calculate_total_rent()
        return total
    
    # find and return a list of tenants that their lease_end is past by the current date
    
    def find_tenants_with_overdue_rent(self) -> list[Tenant]:
        # create a list of tenants with overdue rents
        overdue_tenants = []
        # fetch the current datetime 
        current_date = timezone.now()
        
        # loop through every properties of the lease manager
        for p in self.properties.all():
            # loop through every tenants of that property
            for tenant in p.tenants.all():
                # check if the next payment due date is already past the current date
                if current_date > tenant.next_payment_due:
                    # add the tenant object to the list
                    overdue_tenants.append(tenant)

        return overdue_tenants
    
    def __str__(self) -> str:
        return self.name