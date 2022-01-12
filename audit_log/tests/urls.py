from audit_log_tests import views
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^/$', views.index, name='index'),
    re_path(r'^rate/(\d)/$', views.rate_product, name='rate-product'),
    re_path(r'^category/create/$', views.CategoryCreateView.as_view(), name='category-create'),
    re_path(r'^product/create/$', views.ProductCreateView.as_view(), name='product-create'),
    re_path(r'^product/update/(?P<pk>\d+)/$', views.ProductUpdateView.as_view(), name='product-update'),
    re_path(r'^product/delete/(?P<pk>\d+)/$', views.ProductDeleteView.as_view(), name='product-delete'),
    re_path(r'^extremewidget/create/$', views.ExtremeWidgetCreateView.as_view(), name='extreme-widget-create'),
    re_path(r'^propertyowner/create/$', views.PropertyOwnerCreateView.as_view(), name='property-owner-create'),
    re_path(r'^property/create/$', views.PropertyCreateView.as_view(), name='property-create'),
    re_path(r'^property/update/(?P<pk>\d+)/$', views.PropertyUpdateView.as_view(), name='property-update'),
    re_path(r'^employee/create/$', views.EmployeeCreateView.as_view(), name='employee-create'),
    re_path(r'^employee/update/(?P<pk>\d+)/$', views.EmployeeUpdateView.as_view(), name='employee-update'),
    re_path(r'^item/create/$', views.ItemCreateView.as_view(), name='item-create'),
    re_path(r'^item/update/(?P<pk>\d+)/$', views.ItemUpdateView.as_view(), name='item-update'),
    re_path(r'^special-item/create/$', views.SpecialItemCreateView.as_view(), name='special-item-create'),
    re_path(r'^special-item/update/(?P<pk>\d+)/$', views.SpecialItemUpdateView.as_view(), name='special-item-update'),
]