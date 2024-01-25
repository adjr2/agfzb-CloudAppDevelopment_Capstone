from django.db import models
from django.utils.timezone import now


# Create your models here.
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30, default="")
    description = models.CharField(null=True, max_length=1000, default="")

    def __str__(self):
        return self.name + " " + self.description

car_model_types = [
    ("Sedan", "Sedan"),
    ("SUV", "SUV"),
    ("WAGON", "WAGON")
]
# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    dealer_id = models.IntegerField(null=True)
    name = models.CharField(null=False, max_length=30, default="")
    model_type = models.CharField(null=True, max_length=30, choices=car_model_types)
    year = models.DateField(null=True)

    def __str__(self):
            return self.name + " " + self.model_type

# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
