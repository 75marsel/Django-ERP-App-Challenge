# JammizTechLabsCorp Technical Exam/Coding Challenge

By: Jeric Marcel Gappi

A coding challenge requirement for Jr. Python Engineers position.

Django Full stack using Django, Vanilla HTML, Tailwind CSS and Flowbite.

Currently all buisness logic are held inside the Models but some that is complex are in the controller  (views).

for tailwind use: <br>
    -npm install -D tailwindcss <br>
    -npx tailwindcss init <br>
    -npm install flowbite <br>
    -npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch <br>

There is an addtional model added for extra functionality related to Unit Numbers and future design implementations surrounding Room-related details.

```
class UnitRoom(models.Model):
        unit_number = models.CharField(max_length=10, primary_key=True, unique=True)
        tenant = models.ForeignKey(
            Tenant,
            on_delete=models.CASCADE,
            blank = True,
            null=True,
        )
        property = models.ForeignKey(
            Property,
            on_delete=models.CASCADE,
            blank=True,
            null=True,
        )
        
        def __str__(self):
            return self.unit_number
```

**Challenge: Real Estate ERP** – Multi-Tenant Lease and Revenue Management System <br>
You are tasked with designing and implementing a real estate management system that handles a portfolio of properties, tenants, lease agreements, and financial reporting. The system should support multiple tenants per property, rent schedules, lease renewals, and revenue analytics.

    Classes and Structure:
        Class: Property
    
        Attributes:
            - id: Unique identifier for the property.
            - address: Address of the property (string).
            - property_type: Type of property (e.g., "residential", "commercial").
            - units: Number of rentable units in the property (for multi-unit buildings).
            - tenants: A list of Tenantobjects that are leasing the property.
            <br>
        Methods:
            - __init__: Initializes the property with given attributes.
            - add_tenant: Adds a Tenant to the property, assigning them to a unit.
            - remove_tenant: Removes a Tenant from the property.
            - calculate_occupancy_rate: Calculates the current occupancy rate of the property.
            - calculate_total_rent: Computes total rent collected from the tenants.
            <br>

        Class: Tenant
        
            Attributes:
                - id: Unique identifier for the tenant.
                - name: Name of the tenant (string).
                - lease_start: Lease start date (datetime).
                - lease_end: Lease end date (datetime).
                - monthly_rent: Monthly rent paid by the tenant (float).
                - unit: The unit number occupied by the tenant (string).
                - Methods:
                - __init__: Initializes the tenant with given attributes.
                - renew_lease: Renews the lease for the tenant by extending the end date.
                <br>
    Class: LeaseManager

        Attributes:
            - properties: A list of Property objects being managed.
        Methods:
            - add_property: Adds a Property to the portfolio.
            - remove_property: Removes a Property by its ID.
            - find_vacant_units: Returns a list of properties and the number of vacant units.
            - generate_lease_expiry_report: Provides a report of leases that are expiring within a given timeframe.
            - calculate_total_revenue: Calculates the total monthly rent across all properties.
            - find_tenants_with_overdue_rent: Identifies tenants who have overdue rent based on a hypothetical due date.
        
        
    Additional Requirements:
            - Data Structures: Design appropriate data structures to store and efficiently retrieve information about tenants, leases, and properties.
            - Error Handling: Ensure that the system can handle invalid inputs such as duplicate tenants, leases that overlap for the same unit, and attempts to remove non-existent properties or tenants.
            - Algorithms: Implement algorithms to handle operations such as sorting leases by expiration date, identifying vacant units across properties, and calculating the overall financial performance of the portfolio.


    Bonus (Optional):
            - Lease History: Implement a feature to track the history of leases for each tenant, including past leases and any renewals.
            - Revenue Forecasting: Implement a method that forecasts the revenue for the next 12 months based on existing lease data and possible renewals.
            - Data Persistence: Simulate storing data in a database or using file I/O to save the state of the system.