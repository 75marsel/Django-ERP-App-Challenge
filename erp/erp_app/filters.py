import django_filters
from erp_app.models import Tenant

class TenantFilter(django_filters.FilterSet):
    
    ordering = django_filters.OrderingFilter(
        fields=(
            ('monthly_rent', 'Monthly Rent'),
            # Add other fields you want to sort by
        ),
        label='Order by',
    )
    
    class Meta:
        model = Tenant
        fields = []
        # fields = {
        #     "name": ["icontains"],
        #     "lease_start": ["lte", "gte"],
        #     "lease_end": ["lte", "gte"],
        #     "next_payment_due": ["lte", "gte"],
        #     "monthly_rent": ["lte", "gte"],
        #     "unit": ["icontains"],
        # }