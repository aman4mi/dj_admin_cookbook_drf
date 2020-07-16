from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Category, Origin, Hero, HeroProxy, Villain, HeroAcquaintance, AllEntity
import csv
import sys
from django import forms
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe

MAX_OBJECTS = 1


class EntitiesAdminSite(AdminSite):
         site_header = "E-recruitment Entities Admin 2"
         site_title = "E-recruitment Entities Admin Portal 2"
         index_title = "Welcome to E-recruitment Researcher Entities Portal 2"

entities_admin_site = EntitiesAdminSite(name='entities_admin')

entities_admin_site.register(Category)
entities_admin_site.register(Origin)
entities_admin_site.register(Hero)
entities_admin_site.register(Villain)

class ExportCsvMixin:

    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class ImportCsvMixin:

    pass

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

class HeroAcquaintanceInline(admin.TabularInline):
    model = HeroAcquaintance

class HeroForm(forms.ModelForm):
    category_name = forms.CharField()

    class Meta:
        model = Hero
        exclude = ["category"]

class CategoryChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "Category: {}".format(obj.name)



@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ['name', 'hero_count', 'villain_count']
    # admin.site.register(Origin, OriginAdmin) 

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         _hero_count=Count("hero", distinct=True),
    #         _villain_count=Count("villain", distinct=True),
    #     )
    #     return queryset

    def hero_count(self, obj):
        return obj.hero_set.count()
    def villain_count(self, obj):
        return obj.villain_set.count()   

    # hero_count.admin_order_field = '_hero_count'
    # villain_count.admin_order_field = '_villain_count'  


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
    # create a single Django admin from two different models
    form = HeroForm

    list_display = ("name", "is_immortal", "category", "origin", "children_display")

    # list_display = ("name", "is_immortal", "category", "origin", "is_very_benevolent", "children_display")
    # list_filter = ("is_immortal", "category", "origin", IsVeryBenevolentFilter)
    # actions = ["mark_immortal"] 
    actions = ["export_as_csv"]   
    change_list_template = "entities/heroes_changelist.html"

    # One to One relation as admin inline
    inlines = [HeroAcquaintanceInline]
    raw_id_fields = ["category"]

    # show larger number of rows on listview e.g:250
    # list_per_page = 1

    # disable django admin pagination
    # list_per_page = sys.maxsize

    # date_hierarchy = 'added_on'
    # readonly_fields = ["added_on"]
    # exclude = ['added_by',]

    readonly_fields = ["headshot_image"]

    # add additional actions
    def mark_immortal(self, request, queryset):
        queryset.update(is_immortal=True)


    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'category':
    #         return CategoryChoiceField(queryset=Category.objects.all())
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def headshot_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.headshot.url,
            width=obj.headshot.width,
            height=obj.headshot.height,
            )
    )

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )    

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions    

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('immortal/', self.set_immortal),
            path('mortal/', self.set_mortal),
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def set_immortal(self, request):
        self.model.objects.all().update(is_immortal=True)
        self.message_user(request, "All heroes are now immortal")
        return HttpResponseRedirect("../")

    def set_mortal(self, request):
        self.model.objects.all().update(is_immortal=False)
        self.message_user(request, "All heroes are now mortal")
        return HttpResponseRedirect("../")   

#  create a single Django admin from two different models
    def save_model(self, request, obj, form, change):
        category_name = form.cleaned_data["category_name"]
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        category, _ = Category.objects.get_or_create(name=category_name)
        obj.category = category
        super().save_model(request, obj, form, change)    

    # def has_add_permission(self, request):
    #     if self.model.objects.count() >= 1:
    #         return False
    #     return super().has_add_permission(request)     

    # def has_add_permission(self, request):
    #     return False    

# show many to many or reverse FK fields on listview
    def children_display(self, obj):
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                    args=(child.pk,)),
                child.name)
             for child in obj.children.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"

    children_display.short_description = "Children"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name", "category"]
        else:
            return []


# filter FK dropdown values
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return CategoryChoiceField(queryset=Category.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)









@admin.register(HeroProxy)
class HeroProxyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_immortal", "category", "origin",)
    readonly_fields = ("name", "is_immortal", "category", "origin",)

@admin.register(Villain)
class VillainAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("name", "category", "origin")
    actions = ["export_as_csv"]

    # readonly_fields = ["added_on"]
    change_form_template = "entities/villain_changeform.html"


    def response_change(self, request, obj):
        if "_make-unique" in request.POST:
            matching_names_except_this = self.get_queryset(request).filter(name=obj.name).exclude(pk=obj.id)
            matching_names_except_this.delete()
            obj.is_umique = True
            obj.save()
            self.message_user(request, "This villain is now unique")
            return HttpResponseRedirect(".")
        super().response_change()


class VillainInline(admin.StackedInline):
    model = Villain

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

    inlines = [VillainInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False    


@admin.register(AllEntity)
class AllEntiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")            

    
