# ================= Global Search View =================
from rest_framework import status
from rest_framework.response import Response


# class GlobalSearchAPIView(generics.GenericAPIView):
#     permission_classes = [IsMainManager]
#     authentication_classes = [CustomJWTAuthentication]
#
#     def get(self, request):
#         q = request.query_params.get("q", "").strip()
#
#         if not q or len(q) < 2:
#             return Response({
#                 "crm": [],
#                 "hr": [],
#                 "games": [],
#                 "sony_accounts": [],
#                 "documents": [],
#                 "real_assets": [],
#                 "transactions": [],
#             })
#
#         customers = Customer.objects.filter(
#             is_deleted=False,
#             full_name__icontains=q
#         )[:5]
#
#         employees = Employee.objects.filter(
#             is_deleted=False
#         ).filter(
#             Q(first_name__icontains=q) | Q(last_name__icontains=q)
#         )[:5]
#
#         games = Game.objects.filter(
#             is_deleted=False,
#             title__icontains=q
#         )[:5]
#
#         sony_accounts = SonyAccount.objects.filter(
#             is_deleted=False,
#             username__icontains=q
#         )[:5]
#
#         documents = Document.objects.filter(
#             is_deleted=False,
#             title__icontains=q
#         )[:5]
#
#         real_assets = RealAssets.objects.filter(
#             is_deleted=False,
#             title__icontains=q
#         )[:5]
#
#         transactions = Transaction.objects.filter(
#             is_deleted=False
#         ).filter(
#             Q(payer_str__icontains=q) |
#             Q(receiver_str__icontains=q) |
#             Q(payer__phone__icontains=q) |
#             Q(receiver__phone__icontains=q)
#         )[:5]
#
#         return Response({
#             "crm": CustomerSearchSerializer(customers, many=True).data,
#             "hr": EmployeeSearchSerializer(employees, many=True).data,
#             "games": GameSearchSerializer(games, many=True).data,
#             "sony_accounts": SonyAccountSearchSerializer(sony_accounts, many=True).data,
#             "documents": DocumentSearchSerializer(documents, many=True).data,
#             "real_assets": RealAssetsSearchSerializer(real_assets, many=True).data,
#             # "transactions": TransactionSearchSerializer(transactions, many=True).data,
#         })
#

class SoftDeleteViewMixin:
    """
    View-level mixin for soft delete.
    Delegates the actual deletion to the serializer's destroy() method
    and always returns 204 No Content.
    """
    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
