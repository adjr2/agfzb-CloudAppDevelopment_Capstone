from django.contrib import admin
from .models import CarMake, CarModel


# Register your models here.

class CarModelInLine(admin.StackedInline):
    model = CarModel
    extra = 5

class CarModelAdmin(admin.ModelAdmin):
    fields = ["dealer_id", "name", "model_type", "year"]

class CarMakeAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    inlines = [CarModelInLine]

admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)
