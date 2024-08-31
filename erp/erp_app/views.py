from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.utils.timezone import make_naive
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView # all 
from django.views.generic.detail import DetailView # single
from .models import Property, Tenant, LeaseManager, UnitRoom
from django.contrib import messages
from .forms import (
    PropertyForm, TenantForm, UnitRoomForm, 
    PropertyAddTenantForm, LeaseManagerForm, PropertyAddUnitRoomForm,
    PropertyRemoveTenantForm, PropertyRemoveUnitRoomForm, GenerateLeaseExpiryReportForm,
    AddPropertyToLeaseManagerForm, AddUnitRoomToTenantForm, 
)
from django.utils.dateparse import parse_datetime


def home(request):
    return render(
        request,
        "erp_app/index.html"
    )

# add a property using forms
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "erp_app/forms/property.html"
    
    def get_success_url(self):
        return reverse(
            "property_detail",
            kwargs={
                "pk": self.object.pk,
            }
        )

# removes a property from a lease manager
def property_remove_view(request, lm_id, property_id):
    manager = get_object_or_404(LeaseManager, id=lm_id)
    if request.method == "POST":
            manager.remove_property(property_id)
    
    return redirect('lease_manager_detail', pk=lm_id)

def unit_room_delete_view(request, room_id):
    unit_room = get_object_or_404(UnitRoom, id=room_id)
    property_id = unit_room.property.id
    if request.method == "POST":
        property = Property.objects.get(id=property_id)
        property.remove_tenant(unit_room.tenant)
        unit_room.remove_property()
    
    return redirect('property_detail', pk=property_id)


def tenant_unit_room_remove_view(request, pk):
    try:
        tenant = Tenant.objects.get(id=pk)
        unit_room = UnitRoom.objects.get(unit_number=tenant.unit)
    except UnitRoom.DoesNotExist or Tenant.DoesNotExist:
        messages.warning(request, "Please Check if Tenant has a valid Unit Room!")
    if request.method == "POST":
        if tenant.unit:
            # property = Property.objects.get(tenants=tenant)
            # property.remove_tenant(tenant)
            tenant.remove_unit()
            unit_room.remove_tenant()
            
            messages.success(request, "Removing Tenat's Unit Room success!")
        else:
            messages.error(request, "Tenant does not have a Unit Room!")
    
    return redirect('tenant_detail', pk=pk)
 

# List of all Properties
class PropertyListView(ListView):
    model = Property
    template_name = "erp_app/list/property_list.html"
    context_object_name = "properties"

# Specific detail of a property
# includes property attributes, tenants, rooms
class PropertyDetailView(DetailView):
    model = Property
    template_name = "erp_app/detail/property_detail.html"
    context_object_name = "property"

# Add a tenant to a property
class PropertyAddTenantView(UpdateView):
    model = Property
    form_class = PropertyAddTenantForm
    template_name = "erp_app/forms/property_add_tenant.html"
    
    def get_success_url(self):
        return reverse(
            "property_detail",
            kwargs={
                "pk": self.object.pk,
            }
        )
        
    def get_form_kwargs(self):
        # Get the default form kwargs from the parent class
        kwargs = super().get_form_kwargs()
        # Add property_id to the form kwargs
        kwargs['property_id'] = self.object.id
        return kwargs        

    def form_valid(self, form):
        # Call the parent form_valid method to handle default behavior
        response = super().form_valid(form)
        tenant = form.cleaned_data.get('tenant')
        unit = form.cleaned_data.get("unit")

        # Add tenant to the property’s tenants field
        if tenant and unit:
            try:
                self.object.add_tenant(tenant=tenant, unit_room=unit)
                messages.success(self.request, "Tenant was added to the unit successfuly!")
            except ValueError:
                messages.error(self.request, "All units are occupied!")
                return self.form_invalid(form)


        return response

# Remove a tenant to a property
class PropertyRemoveTenantView(UpdateView):
    model = Property
    form_class = PropertyRemoveTenantForm
    template_name = "erp_app/forms/property_remove_tenant.html"
    
    def get_success_url(self):
        return reverse(
            "property_detail",
            kwargs={
                "pk": self.object.pk,
            }
        )
        
    def get_form_kwargs(self):
        # Get the default form kwargs from the parent class
        kwargs = super().get_form_kwargs()
        # Add property_id to the form kwargs
        kwargs['property_id'] = self.object.id
        return kwargs   
        
    def form_valid(self, form):
        # Call the parent form_valid method to handle default behavior
        response = super().form_valid(form)
        tenant = form.cleaned_data.get('tenant')
        # print(tenant)
        # Add tenant to the property’s tenants field
        if tenant:
            self.object.remove_tenant(tenant)
            # self.object.tenants.remove(tenant)
            # self.object.save()

        return response

# Add a room to a property
class PropertyAddUnitRoomView(UpdateView):
    model = Property
    form_class = PropertyAddUnitRoomForm
    template_name = "erp_app/forms/property_add_room.html"
    
    def get_success_url(self):
        return reverse(
            "property_detail",
            kwargs={
                "pk": self.object.pk,
            }
        )
        
    def get_form_kwargs(self):
        # Get the default form kwargs from the parent class
        kwargs = super().get_form_kwargs()
        # Add property_id to the form kwargs
        kwargs['property_id'] = self.object.id
        return kwargs
        
    def form_valid(self, form):
        # Call the parent form_valid method to handle default behavior
        response = super().form_valid(form)
        unit_room = form.cleaned_data.get('unit_room')

        # Get the current property instance using the pk from the URL
        property_instance = self.get_object()

        # Add room to the property
        if unit_room:
            try:
                property_instance.add_room(unit_room)
                messages.success(self.request, "Unit Room added was added to the Property!")
            except ValueError:
                messages.error(self.request, "Property Units already full!")

        return response
    
# add a tenant using form
class TenantCreateView(CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = "erp_app/forms/tenant.html"
    
    def get_success_url(self):
        return reverse("tenant_detail_all")

# Add a unit room to a property using form (WILL CHANGE URL TO unit_room_form)
class UnitRoomCreateView(CreateView):
    model = UnitRoom
    form_class = UnitRoomForm
    template_name = "erp_app/forms/unit_room_form.html"
    success_url = reverse_lazy("property_view_all")

# Deletes a unit room in the database
def delete_unit_room_view(request, property_id, id):
    try:
        unit_room = get_object_or_404(UnitRoom, id=id)
    except Exception as e:
        messages.warning(request, "Unit Room not found!")
        
    if request.method == "POST":
        if unit_room:
            unit_room.delete()
            messages.success(request, "Unit Room Successfuly deleted!")
        else:
            messages.error(request, "Error Deleting Unit Room!")
    
    return redirect('property_detail', pk=property_id)

# deletes a property in the database 
def property_delete_view(request, property_id):
    try:
        property = get_object_or_404(Property, id=property_id)
    except Exception as e:
        messages.warning(request, "Property not found!")
        
    if request.method == "POST":
        if property:
            property.delete_property()
            messages.success(request, "Property Successfuly deleted!")
        else:
            messages.error(request, "Error Deleting Property!")
    
    return redirect('property_view_all')

# deletes the tenant object
def tenant_delete_view(request, tenant_id):
    try:
        tenant = get_object_or_404(Tenant, id=tenant_id)
    except Exception as e:
        messages.warning(request, "Tenant not found!")
        
    if request.method == "POST":
        if tenant:
            tenant.delete()
            messages.success(request, "Tenant Successfuly deleted!")
        else:
            messages.error(request, "Error Deleting Tenant!")
    
    return redirect('tenant_detail_all')

# list of all tenants (WILL CHANGE URL TO tenant)
class TenantListView(ListView):
    model = Tenant
    template_name = "erp_app/list/tenant_list.html"
    context_object_name = "tenants"

# Specific detail of a tenant
class TenantDetailView(DetailView):
    model = Tenant
    template_name = "erp_app/detail/tenant_detail.html"
    context_object_name = "tenant"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_add'] = AddUnitRoomToTenantForm(property=self.object.properties.all(), prefix="form_add")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_add = AddUnitRoomToTenantForm(request.POST, property=self.object.properties.all(), prefix="form_add")

        if "form_add" in request.POST and form_add.is_valid():
            if self.object.unit == "":
                unit_room = UnitRoom.objects.get(id=form_add.cleaned_data["unit_room"].id)
                unit_room.add_tenant(self.object)
                self.object.add_unit(unit_room.unit_number)
                messages.success(request, "Adding a Unit Room to Tenat success!")
            else:
                messages.error(request, "Error Adding a Unit Room!")
        
        return self.render_to_response(self.get_context_data(form=form_add))
    

# A VIEW FOR UPDATING THE LEASE END DATETIME OF A TENANT
class TenantRenewLeaseView(View):
    def post(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)
        selected_lease_end = request.POST.get("lease_end")
        if selected_lease_end:
            extended_date = parse_datetime(selected_lease_end)
            tenant.renew_lease(extended_date)
            tenant.save()
        return redirect(reverse('tenant_detail', args=[tenant.id]))
    

# add a lease manager using forms
class LeaseManagerCreateView(CreateView):
    model = LeaseManager
    form_class = LeaseManagerForm
    template_name = "erp_app/forms/lease_manager_form.html"
    
# delete a lease manager
def lease_manager_remove_view(request, id):
    try:
        lease_manager = get_object_or_404(LeaseManager, id=id)
    except Exception as e:
        messages.warning(request, "Lease Manager not found!")
        
    if request.method == "POST":
        if lease_manager:
            lease_manager.delete()
            messages.success(request, "Lease Manager Successfuly deleted!")
        else:
            messages.error(request, "Error Deleteing Lease Manager!")
    
    return redirect('lease_manager_view')

        
def lease_manager_view(request):
    if request.method == "POST":
        form = LeaseManagerForm(request.POST, prefix="form")
        if "form" in request.POST and form.is_valid():
            form.save()
            messages.success(request, 'Lease Manager added successfully!')
            return redirect('lease_manager_view')
        else:
            messages.error(request, 'Please correct the errors below.')
            # print(form.is_valid())

    else:
        form = LeaseManagerForm(prefix="form")

    lease_manager = LeaseManager.objects.all()  # Get all LeaseManager instances
    properties = Property.objects.all()  # Get all Property instances
    
    context = {
        "form": form,
        "lease_manager": lease_manager,
        'properties': properties,
    }
    
    return render(request, "erp_app/list/lease_manager_list.html", context)


def generate_report_view(request, id):
    property = get_object_or_404(Tenant, id=id)
    return render(
        request,
        "erp_app/reports/property_report.html",
        {"property": property},
    )
    
    
# Specific detail of a lease manager
# includes property attributes, tenants, rooms
class LeaseManagerDetailView(DetailView):
    model = LeaseManager
    template_name = "erp_app/detail/manager_detail.html"
    context_object_name = "manager"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GenerateLeaseExpiryReportForm(lease_manager=self.object, prefix="form")
        context["form_add"] = AddPropertyToLeaseManagerForm(lease_manager=self.object, prefix="form_add")
        context["total_revenue"] = self.get_object().calculate_total_revenue()
        self.get_object().find_tenants_with_overdue_rent()
        # print(context['form_add'])
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = GenerateLeaseExpiryReportForm(request.POST, lease_manager=self.object, prefix="form")
        form_add = AddPropertyToLeaseManagerForm(request.POST, lease_manager=self.object, prefix="form_add") 
        
        if "form" in request.POST and form.is_valid():
            start_lease_date = make_naive(form.cleaned_data['lease_start'])
            end_lease_date =  make_naive(form.cleaned_data['lease_end'])
            tenants = self.object.generate_lease_expiry_report(
                start_lease_date=start_lease_date, 
                end_lease_date=end_lease_date,
                properties=form.cleaned_data["properties"],
                )
               
            if tenants:
                properties = Property.objects.filter(tenants__in=tenants).distinct()
                
                context = {
                    'tenants': tenants,
                    'properties': properties,
                    'lease_manager_id': self.object.id,
                }
                
                return render(
                    request, 
                    'erp_app/reports/property_report.html', 
                    context,
                )
        elif "form_add" in request.POST and form_add.is_valid():
            self.object.add_property(form_add.cleaned_data["properties"])
            # messages.success(request, 'Lease Expiry Report generated successfully!')
            # return redirect('lease_manager_report_view', id=properties_id.id)

        return self.render_to_response(self.get_context_data(form=form))
    
    
def find_vacant_units_view(request, manager_id):
    lease_manager = LeaseManager.objects.get(id=manager_id)
    property = lease_manager.find_vacant_units()
  
    return render(
        request,
        "erp_app/reports/vacant_units.html",
        { "properties": property,},
    )

def find_tenants_with_overdue_rent_view(request, manager_id):
    lease_manager = LeaseManager.objects.get(id=manager_id)
    tenants = lease_manager.find_tenants_with_overdue_rent()
  
    return render(
        request,
        "erp_app/reports/overdue_rent.html",
        { "tenants": tenants,},
    )
    

def calculate_total_revenue_view(manager_id):
    lease_manager = LeaseManager.objects.get(id=manager_id)
    total = 0
    for p in lease_manager.properties.all():
        total += p.calculate_total_rent()
    return total