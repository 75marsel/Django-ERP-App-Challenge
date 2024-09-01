from rest_framework import serializers
from erp_app.models import Tenant, Property

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "lease_start",
            "lease_end",
            "next_payment_due",
            "monthly_rent",
            "unit",
        ]


class PropertySerializer(serializers.ModelSerializer):
    occupancy_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            "id",
            "address",
            "property_type",
            "units",
            "current_units",
            "tenants",
            "occupancy_rate",
        ]
    
    def get_occupancy_rate(self, obj):
        return obj.calculate_occupancy_rate()