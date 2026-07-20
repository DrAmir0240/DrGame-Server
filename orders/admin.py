from django.contrib import admin

from orders.models import ProductOrderCategory, ProductOrderStage, ProductOrder, ProductOrderStageAction, \
    ProductOrderItem, ProductOrderStageLog, SonyAccountOrderCategory, SonyAccountOrderStage, \
    SonyAccountOrderStageAction, SonyAccountOrder, SonyAccountOrderConsole, SonyAccountOrderItem, \
    SonyAccountOrderStageLog, SonyAccountOrderActionLog, RepairOrderStage, RepairOrderStageAction, RepairOrder, \
    RepairOrderDevice, RepairOrderStageLog, RepairOrderCategory, RepairOrderActionLog


@admin.register(ProductOrderCategory)
class ProductOrderCategoryAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(ProductOrderStage)
class ProductOrderStageAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(ProductOrderStageAction)
class ProductOrderStageActionAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(ProductOrderItem)
class ProductOrderItemAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(ProductOrderStageLog)
class ProductOrderStageLogAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderCategory)
class SonyAccountOrderCategoryAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderStage)
class SonyAccountOrderStageAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderStageAction)
class SonyAccountOrderStageActionAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrder)
class SonyAccountOrderAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderConsole)
class SonyAccountOrderConsoleAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderItem)
class SonyAccountOrderItemAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderStageLog)
class SonyAccountOrderStageLogAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(SonyAccountOrderActionLog)
class SonyAccountOrderActionLogAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderCategory)
class RepairOrderCategoryAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderStage)
class RepairOrderStageAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderStageAction)
class RepairOrderStageActionAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderDevice)
class RepairOrderDeviceAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderStageLog)
class RepairOrderStageLogAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"


@admin.register(RepairOrderActionLog)
class RepairOrderActionLogAdmin(admin.ModelAdmin):
    class Meta:
        fields = "__all__"
        search_fields = "__all__"
