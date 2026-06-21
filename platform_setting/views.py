# # Create your views here.
# from rest_framework import generics
# from management.serializers import ManagementSonyAccountSerializer, ManagementProductCategorySerializer, \
#     ManagementProductSerializer, ManagementEmployeeSerializer, ManagementRepairmanSerializer, ManagementCustomerSerializer, ManagementBusinessCustomerSerializer, \
#     ManagementEmployeeCreateSerializer, ManagementProductAddSerializer, ManagementProductColorSerializer, \
#     ManagementProductCompanySerializer, ManagementOrderSerializer
# from crm.models import Customer, BusinessCustomer
# from hr.models import Employee, Repairman
# from accounting.models import Transaction, TransactionType, Order
# from storage.models import SonyAccount, ProductCategory, ProductColor, ProductCompany
#
#
# # get method api list
# class EmployeeListAPIView(generics.ListAPIView):
#     queryset = Employee.objects.all()
#     serializer_class = ManagementEmployeeSerializer
#
#
# class EmployeeDetailAPIView(generics.RetrieveAPIView):
#     queryset = Employee.objects.all()
#     serializer_class = ManagementEmployeeSerializer
#     lookup_field = 'pk'
#
#
# class RepairmanListAPIView(generics.ListAPIView):
#     queryset = Repairman.objects.all()
#     serializer_class = ManagementRepairmanSerializer
#
#
# class RepairmanDetailAPIView(generics.RetrieveAPIView):
#     queryset = Repairman.objects.all()
#     serializer_class = ManagementRepairmanSerializer
#     lookup_field = 'pk'
#
#
# class CustomerListAPIView(generics.ListAPIView):
#     queryset = Customer.objects.all()
#     serializer_class = ManagementCustomerSerializer
#
#
# class CustomerDetailAPIView(generics.RetrieveAPIView):
#     queryset = Customer.objects.all()
#     serializer_class = ManagementCustomerSerializer
#     lookup_field = 'pk'
#
#
# class BusinessCustomerListAPIView(generics.ListAPIView):
#     queryset = BusinessCustomer.objects.all()
#     serializer_class = ManagementBusinessCustomerSerializer
#
#
# class BusinessCustomerDetailAPIView(generics.RetrieveAPIView):
#     queryset = BusinessCustomer.objects.all()
#     serializer_class = ManagementBusinessCustomerSerializer
#     lookup_field = 'pk'
#
#
# class SonyAccountListAPIView(generics.ListAPIView):
#     queryset = SonyAccount.objects.all()
#     serializer_class = ManagementSonyAccountSerializer
#
#
# class SonyAccountDetailAPIView(generics.RetrieveAPIView):
#     queryset = SonyAccount.objects.all()
#     serializer_class = ManagementSonyAccountSerializer
#     lookup_field = 'pk'
#
#
# class ProductCategoryListAPIView(generics.ListAPIView):
#     queryset = ProductCategory.objects.all()
#     serializer_class = ManagementProductCategorySerializer
#
#
# class ProductColorListAPIView(generics.ListAPIView):
#     queryset = ProductColor.objects.all()
#     serializer_class = ManagementProductColorSerializer
#
#
# class ProductCompanyListAPIView(generics.ListAPIView):
#     queryset = ProductCompany.objects.all()
#     serializer_class = ManagementProductCompanySerializer
#
#
# class ProductDetailAPIView(generics.RetrieveAPIView):
#     queryset = ProductCategory.objects.all()
#     serializer_class = ManagementProductSerializer
#     lookup_field = 'pk'
#
#
# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.all()
#     serializer_class = ManagementOrderSerializer
#
#
# class OrderDetailAPIView(generics.RetrieveAPIView):
#     queryset = Order.objects.all()
#     serializer_class = ManagementOrderSerializer
#     lookup_field = 'pk'
#
#
# class TransactionListAPIView(generics.ListAPIView):
#     queryset = TransactionType.objects.all()
#     serializer_class = ManagementProductCategorySerializer
#
#
# class TransactionDetailAPIView(generics.RetrieveAPIView):
#     queryset = Transaction.objects.all()
#     serializer_class = ManagementProductSerializer
#     lookup_field = 'pk'
#
#
# # create method api list
# class EmployeeAddAPIView(generics.CreateAPIView):
#     queryset = Employee.objects.all()
#     serializer_class = ManagementEmployeeCreateSerializer
#
#
# class RepairmanAddAPIView(generics.CreateAPIView):
#     # قابل ساخت با پنل پیامکی
#     pass
#
#
# class CustomerAddAPIView(generics.CreateAPIView):
#     # قابل ساخت با پنل پیامکی
#     pass
#
#
# class BusinessCustomerAddAPIView(generics.CreateAPIView):
#     # قابل ساخت با پنل پیامکی
#     pass
#
#
# class SonyAccountAddAPIView(generics.CreateAPIView):
#     queryset = SonyAccount.objects.all()
#     serializer_class = ManagementSonyAccountSerializer
#
#
# class ProductAddAPIView(generics.CreateAPIView):
#     queryset = ProductCategory.objects.all()
#     serializer_class = ManagementProductAddSerializer
