from django import forms
from django.db.models import Q
from .models import Property, Tenant, UnitRoom, LeaseManager

FORM_STYLE = (
    "block w-full px-3 py-2 text-gray-900 placeholder-gray-400 "
    "border border-gray-300 rounded-lg shadow-sm focus:outline-none "
    "focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm "
    "dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white "
    "dark:focus:ring-blue-500 dark:focus:border-blue-500"
)



class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "address",
            "property_type",
            "units",
        ]
        labels = {
            "address": "Property Address",
            "property_type": "Property Type",
            "units": "Number of Units",
        }
        
        FORM_STYLE = "block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
        
        widgets = {
            "address": forms.TextInput(attrs={
                "placeholder": "Test highway Sample Street",
                "class": FORM_STYLE,
            }),
            "property_type": forms.Select(attrs={
                "placeholder": "Select a Property Type",
                "class": FORM_STYLE,
            }),
            "units": forms.NumberInput(attrs={
                "placeholder": "e.g 10",
                "class": FORM_STYLE,
            }),
        }
        
class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            "name",
            "lease_start",
            "lease_end",
            "monthly_rent",
        ]
        labels = {
            "name": "Tenant Name",
            "lease_start": "Start Lease Date",
            "lease_end": "End Lease Date",
            "monthly_rent": "Monthly Rent",
        }
        
        FORM_STYLE = "block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
        
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Test highway Sample Street",
                "class": FORM_STYLE,
            }),
            "lease_start": forms.DateTimeInput(attrs={
                "placeholder": "Lease Start",
                "class": "form-control",
                "type": "datetime-local",
                "class": FORM_STYLE,
            }),
            "lease_end": forms.DateTimeInput(attrs={
                "placeholder": "Lease End",
                "class": "form-control",
                "type": "datetime-local",
                "class": FORM_STYLE,
            }),
            "monthly_rent": forms.NumberInput(attrs={
                "placeholder": "e.g 500",
                "class": FORM_STYLE,
            }),
        }
    
        
class UnitRoomForm(forms.ModelForm):
    unit_number = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "AB-01",
            "class": FORM_STYLE,
        }),
        required=True
    )
    # property = forms.ModelChoiceField(
    #     queryset=Property.objects.all(),  # Get choices from the Property model
    #     widget=forms.Select(attrs={
    #         "placeholder": "Property",
    #         "class": FORM_STYLE,
    #     }),
    #     required=True
    # )
    # tenant = forms.ModelChoiceField(
    #     queryset=Tenant.objects.all(),  # Get choices from the Tenant model
    #     widget=forms.Select(attrs={
    #         "placeholder": "Tenant",
    #         "class": FORM_STYLE,
    #     }),
    #     required=False
    # )
    

    class Meta:
        model = UnitRoom
        fields = [
            "unit_number",
            # "property",
            # "tenant",
        ]
        labels = {
            "unit_number": "Unit Number",
            # "property": "Property",
            # "tenant": "Tenant",
        }
    
    def clean_unit_number(self):
        unit_number = self.cleaned_data.get('unit_number')
        if UnitRoom.objects.filter(unit_number=unit_number).exists():
            raise forms.ValidationError("A unit with this number already exists.")
        return unit_number
    

class PropertyAddTenantForm(forms.ModelForm):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),  # Get choices from the Tenant`` model
        widget=forms.Select(attrs={
            "placeholder": "Tenant",
            "class": FORM_STYLE,
        }),
        required=True,
    )
    unit = forms.ModelChoiceField(
        queryset=UnitRoom.objects.none(),  # Get choices from the Unit`` model
        widget=forms.Select(attrs={
            "placeholder": "Unit",
            "class": FORM_STYLE,
        }),
        required=True,
    )
    
    class Meta:
        model = Property
        fields = [
            "tenant",
            "unit",
        ]
        
        labels = {
            "tenant": "Tenant",
            "unit": "Unit",
        }
    
    def clean_tenant(self):
        tenant = self.cleaned_data.get('tenant')
        if tenant and Property.objects.filter(tenants=tenant).exists():
            raise forms.ValidationError("This tenant is already assigned to a property.")
        
        return tenant
        
    def __init__(self, *args, **kwargs):
        property_id = kwargs.pop('property_id', None)  # Extract property_id from kwargs
        super().__init__(*args, **kwargs)
        
        if property_id:
            # Filter the queryset based on the property_id
            self.fields['tenant'].queryset = Tenant.objects.filter(
                properties__isnull=True
                )
            self.fields['unit'].queryset = UnitRoom.objects.filter(
                property_id=property_id, 
                tenant__isnull=True
                )
            

class PropertyRemoveTenantForm(forms.ModelForm):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.none(),  # Get choices from the Tenant`` model
        widget=forms.Select(attrs={
            "placeholder": "Tenant",
            "class": FORM_STYLE,
        }),
        required=True,
    )
    
    class Meta:
        model = Property
        fields = [
            "tenant",
        ]
        
        labels = {
            "tenant": "Tenant",
        }
        
    def __init__(self, *args, **kwargs):
        property_id = kwargs.pop('property_id', None)  # Extract property_id from kwargs
        super().__init__(*args, **kwargs)
        
        if property_id:
            # Filter the queryset based on the property_id
            self.fields['tenant'].queryset = Tenant.objects.filter(
                properties=Property.objects.get(id=property_id)
                )
            

    
class PropertyAddUnitRoomForm(forms.ModelForm):
    unit_room = forms.ModelChoiceField(
        queryset=UnitRoom.objects.none(),  # Get choices from the Tenant`` model
        widget=forms.Select(attrs={
            "placeholder": "Unit Room",
            "class": FORM_STYLE,
        }),
        required=False
    )
    
    class Meta:
        model = Property
        fields = [
            "unit_room",
        ]
        
        labels = {
            "unit_room": "Unit Room",
        }
    
    def clean_tenant(self):
        unit_room = self.cleaned_data.get('unit_room')
        if unit_room and Property.objects.filter(unit_rooms=unit_room).exists():
            raise forms.ValidationError("This Room is already assigned to a property.")
        
        return unit_room
    
    def __init__(self, *args, **kwargs):
        property_id = kwargs.pop('property_id', None)  # Extract property_id from kwargs
        super().__init__(*args, **kwargs)
        
        if property_id:
            # Filter the queryset based on the property_id
            self.fields['unit_room'].queryset = UnitRoom.objects.filter(property__isnull=True)
    
    
class PropertyRemoveUnitRoomForm(forms.ModelForm):
    unit_room = forms.ModelChoiceField(
        queryset=UnitRoom.objects.none(),  # Start with no choices
        widget=forms.Select(attrs={
            "placeholder": "Unit Room",
            "class": FORM_STYLE,
        }),
        required=False
    )
    
    class Meta:
        model = Property
        fields = [
            "unit_room",
        ]
        
        labels = {
            "unit_room": "Unit Room",
        }
    
    def __init__(self, *args, **kwargs):
        property_id = kwargs.pop('property_id', None)  # Extract property_id from kwargs
        super().__init__(*args, **kwargs)
        
        if property_id:
            # Filter the queryset based on the property_id
            self.fields['unit_room'].queryset = UnitRoom.objects.filter(property_id=property_id)
    

class LeaseManagerForm(forms.ModelForm):
    properties = forms.ModelMultipleChoiceField(
        queryset=Property.objects.none(),
        widget=forms.SelectMultiple(attrs={
            "placholder": "Properties",
            "class": FORM_STYLE,
        }),
    )
    class Meta:
        model = LeaseManager
        fields = ['name', 'properties']

    def clean_properties(self):
        properties = self.cleaned_data.get('properties')

        if properties:
            # Get the IDs of the properties being submitted
            property_ids = properties.values_list('id', flat=True)

            # Check if these properties are already assigned to another Lease Manager
            # Exclude the current LeaseManager instance from the check
            if Property.objects.filter(id__in=property_ids, lease_manager__isnull=False).exists():
                raise forms.ValidationError("One or more properties are already assigned to another Lease Manager.")
        
        return properties
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['properties'].queryset = Property.objects.filter(lease_manager__isnull=True)


class GenerateLeaseExpiryReportForm(forms.ModelForm):
    properties = forms.ModelChoiceField(
        queryset=Property.objects.none(),  # Start with an empty queryset
        widget=forms.Select(attrs={
            "placeholder": "Properties",
            "class": FORM_STYLE,  # Replace FORM_STYLE with actual class if needed
        }),
        empty_label=None,
    )
    lease_start = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local', 
            "class": FORM_STYLE,
            }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    lease_end = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local', 
            "class": FORM_STYLE,
            }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = LeaseManager
        fields = ['properties']

    def __init__(self, *args, **kwargs):
        lease_manager = kwargs.pop('lease_manager', None)  # Get the LeaseManager instance from kwargs
        super().__init__(*args, **kwargs)
        if lease_manager:
            # Filter the properties queryset based on the related properties of the LeaseManager instance
            self.fields['properties'].queryset = lease_manager.properties.all()


class AddPropertyToLeaseManagerForm(forms.ModelForm):
    properties = forms.ModelChoiceField(
        queryset=Property.objects.none(),  # Start with an empty queryset
        widget=forms.Select(attrs={
            "placeholder": "Properties",
            "class": FORM_STYLE,  # Replace FORM_STYLE with actual class if needed
        }),
        empty_label=None,
        required=True,
    )

    class Meta:
        model = LeaseManager
        fields = ['properties']

    def __init__(self, *args, **kwargs):
        lease_manager = kwargs.pop('lease_manager', None)  # Get the LeaseManager instance from kwargs
        super().__init__(*args, **kwargs)
        if lease_manager:
            # Filter the properties queryset based on the related properties of the LeaseManager instance
            self.fields['properties'].queryset = Property.objects.filter(lease_manager=None)
            # print("hi")
            # print(self.fields['properties'].queryset)
            # lease_manager.properties.all()
            

class AddUnitRoomToTenantForm(forms.ModelForm):
    unit_room = forms.ModelChoiceField(
        queryset=UnitRoom.objects.none(),  # Start with an empty queryset
        widget=forms.Select(attrs={
            "placeholder": "Unit Room",
            "class": FORM_STYLE,  # Replace FORM_STYLE with actual class if needed
        }),
        empty_label=None,
    )

    class Meta:
        model = LeaseManager
        fields = ['unit_room']

    def __init__(self, *args, **kwargs):
        property = kwargs.pop('property', None)
        super().__init__(*args, **kwargs)

        if property:
            for p in property:            
                self.fields['unit_room'].queryset = UnitRoom.objects.filter(property=p)