from rest_framework import serializers
from erp_app.models import Tenant

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