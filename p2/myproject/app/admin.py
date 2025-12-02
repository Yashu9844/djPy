from django.contrib import admin

# Register your models here.
from .models import Chai, ChaiReview , Store, ChaiCertification


class ChaiReviewInline(admin.TabularInline):
    model = ChaiReview
    extra = 2

class ChaiAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'type', 'date_added')
    inlines = [ChaiReviewInline]
    
class storeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    filter_horizontal = ('chais',)

class ChaiCertificationAdmin(admin.ModelAdmin):
    list_display = ('chai', 'certified_by', 'certification_date', 'valid_until')


admin.site.register(Chai,ChaiAdmin)
admin.site.register(ChaiReview)
admin.site.register(Store,storeAdmin)
admin.site.register(ChaiCertification,ChaiCertificationAdmin)