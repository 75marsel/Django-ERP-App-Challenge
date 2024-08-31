from django.contrib import admin
from .models import Property, Tenant, UnitRoom, LeaseManager


class UnitRoomInline(admin.TabularInline):
    model = UnitRoom
    extra = 1  # Number of empty forms to show by default

class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "address",
        "property_type",
        "display_tenants",
        "display_total_rent",
        "display_occupancy_rate",
    )

    """
    params: obj - the model that will be using
    """
    
    def display_tenants(self, obj):
        return ', '.join(tenant.name for tenant in obj.tenants.all())
    display_tenants.short_description = 'Tenants'
    
    def display_total_rent(self, obj):
        return obj.calculate_total_rent()
    display_total_rent.short_description = "Total Rent"
    
    def display_occupancy_rate(self, obj):
        return str(obj.calculate_occupancy_rate()) + "%"
    display_occupancy_rate.short_description = "Occupancy Rate"
    

    inlines = [UnitRoomInline]

admin.site.register(UnitRoom)
admin.site.register(Tenant)
admin.site.register(LeaseManager)
# register the Property model to the PropertyAdmin as obj
admin.site.register(Property, PropertyAdmin)