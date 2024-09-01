from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    
    # list of all properties
    path("property/", views.PropertyListView.as_view(), name="property_view_all"),
    
    # Add a property using form
    path("property_form/", views.PropertyCreateView.as_view(), name="property_view"),
   
    # DELETES a property in the database
    path("property_form/delete/<int:property_id>", views.property_delete_view, name="property_delete_view"),
    
    # Remove a property using form
    path("property_form/remove/<int:lm_id>/<int:property_id>/", views.property_remove_view, name="property_remove_view"),
    
    # Add a tenant to a property
    # CHANGE THE LINK TO success/<int:pk>/add_tenant
    path("property_form/<int:pk>/add_tenant/", views.PropertyAddTenantView.as_view(), name="property_add_tenant_view"),
    
    # remove a tenant to a property
    path("property_form/<int:pk>/remove_unit_tenant/", views.PropertyRemoveTenantView.as_view(), name="property_remove_tenant_view"),
    
    # add a room to a property
    path("property_form/<int:pk>/add_unit_room/", views.PropertyAddUnitRoomView.as_view(), name="property_add_unit_room_view"),
    
    # Delete a unit room from a property 
    path("property/<int:property_id>/delete_room/<int:id>", views.delete_unit_room_view, name="delete_unit_room_view"),
    
    # Specific detail of a property
    # includes property attributes, tenants, rooms
    path("property/<int:pk>", views.PropertyDetailView.as_view(), name="property_detail"),
    
    # add a tenant using form (WILL CHANGE URL TO tenant_form)
    path("tenant/", views.TenantCreateView.as_view(), name="tenant_view"),
    
    # list of all tenants (WILL CHANGE URL TO tenant)
    path("tenant/list/", views.TenantListView.as_view(), name="tenant_detail_all"),
    
    # Specific detail of a tenant
    path("tenant/profile/<int:pk>/", views.TenantDetailView.as_view(), name="tenant_detail"),
    
    # DELETES a Tenant in the database
    path("tenant/delete/<int:tenant_id>", views.tenant_delete_view, name="tenant_delete_view"),
    
    # Remove the room of the tenant
    path("tenant/profile/<int:pk>/remove_room/", views.tenant_unit_room_remove_view, name="tenant_remove_room_detail"),
    
    # A VIEW FOR UPDATING THE LEASE END DATETIME OF A TENANT
    path("tenant/profile/<int:tenant_id>/renew_lease/", views.TenantRenewLeaseView.as_view(), name="renew_lease"),
    
    # Add a unit room to a property using form (WILL CHANGE URL TO unit_room_form)
    path("unit_room/", views.UnitRoomCreateView.as_view(), name="unit_room_view"),
    


    # Remove a unit room from a property using form (WILL CHANGE URL TO unit_room_form)
    path("property_form/remove/<int:room_id>/", views.unit_room_delete_view, name="unit_room_remove_view"),
    
    # LEASE MAANGER
    path("manager/", views.lease_manager_view, name="lease_manager_view"),
    
    # Add a Lease Manager using form
    path("manager_form/", views.LeaseManagerCreateView.as_view(), name="lease_manager_create_view"),
    
    # Remove a Lease Manager using form
    path("manager_form/remove/<int:id>", views.lease_manager_remove_view, name="lease_manager_remove_view"),
    
    # FOR Lease Manager generate_lease_expiry_report method
    path("manager/report/<int:id>", views.generate_report_view, name="lease_manager_report_view"),
    
    # Specific detail of a property
    # includes property attributes, tenants, rooms
    path("manager/detail/<int:pk>/", views.LeaseManagerDetailView.as_view(), name="lease_manager_detail"),
    
    # Find vacant properties in the specific manager
    path("manager/detail/<int:manager_id>/find_vacant/", views.find_vacant_units_view, name="find_vacant_units_view"),
    
    # calculate total revenue towards every property of the lease manager
    # path("manager/detail/<int:pk>/revenue", views.calculate_total_revenue_view, name="total_revenue_view"),

    # overdue rent 
    path("manager/detail/<int:manager_id>/overdue/", views.find_tenants_with_overdue_rent_view, name="find_overdue_view"),

    # API Endpoint
    path("api/", views.TenantListAPIView.as_view(), name="tenant-api"),
]
