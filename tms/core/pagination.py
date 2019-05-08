from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'per_page'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    """
    Used as a standard pagination in this project
    """
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 50

    def get_paginated_response(self, data):
        """
        Customize pagination response style in order to work with vuetable
        """
        per_page = self.page.paginator.per_page
        total = self.page.paginator.count
        page_number = int(
            self.request.query_params.get(self.page_query_param, 1)
        )
        bottom = (page_number - 1) * per_page
        top = bottom + per_page
        if top >= total:
            top = total

        return Response({
            'total': total,
            'from': bottom + 1,
            'to': top,
            'per_page': per_page,
            'current_page': page_number,
            'last_page': self.page.paginator.num_pages,
            'next_page_url': self.get_next_link(),
            'prev_page_url': self.get_previous_link(),
            'data': data
        })
