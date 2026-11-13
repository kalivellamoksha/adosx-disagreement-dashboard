from decimal import Decimal, InvalidOperation

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reconciliation.services import find_disagreements


@api_view(["GET"])
def disagreements_view(request):
    org_id = settings.ADOSX_TENANT_ID

    requested_org = request.query_params.get("org_id")

    if requested_org and requested_org != org_id:
        return Response(
            {"error": "Access denied for this organization"},
            status=403
        )

    disagreements = find_disagreements(org_id)

    reason = request.query_params.get("reason", "")
    sort = request.query_params.get("sort", "asc")

    if reason:
        disagreements = [
            issue
            for issue in disagreements
            if issue["reason"] == reason
        ]

    if sort not in ("asc", "desc"):
        return Response(
            {"error": "Invalid sort direction"},
            status=400
        )

    def sort_value(issue):
        value = issue["system_a_value"]

        if value is None:
            value = issue["system_b_value"]

        if value is None:
            return Decimal("-Infinity")

        try:
            amount = Decimal(str(value).replace(",", "").strip())

            if not amount.is_finite():
                return Decimal("-Infinity")

            return amount

        except InvalidOperation:
            return Decimal("-Infinity")

    disagreements.sort(
        key=sort_value,
        reverse=(sort == "desc")
    )

    return Response({
        "org_id": org_id,
        "count": len(disagreements),
        "disagreements": disagreements
    })