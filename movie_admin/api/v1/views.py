from typing import Type

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet, Value
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]
    paginate_by = 50

    def get_queryset(self) -> Type[QuerySet]:
        return (
            Filmwork.objects.all()
            .values(
                "id",
                "title",
                "description",
                "creation_date",
                "rating",
                "type",
            )
            .annotate(
                genres=ArrayAgg("genres__name", distinct=True, default=Value([])),
                actors=ArrayAgg(
                    "person_roles__person__full_name",
                    distinct=True,
                    filter=Q(person_roles__role="actor"),
                    default=Value([]),
                ),
                directors=ArrayAgg(
                    "person_roles__person__full_name",
                    distinct=True,
                    filter=Q(person_roles__role="director"),
                    default=Value([]),
                ),
                writers=ArrayAgg(
                    "person_roles__person__full_name",
                    distinct=True,
                    filter=Q(person_roles__role="writer"),
                    default=Value([]),
                ),
            )
        )

    def render_to_response(self, context: dict, **response_kwargs) -> str:
        return JsonResponse(context)


@method_decorator(staff_member_required, name='dispatch')
class MoviesListApi(MoviesApiMixin, BaseListView):
    """API для списка фильмов."""

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        queryset = self.get_queryset()
        print(self.args)
        print(self.kwargs)
        page_size = self.get_paginate_by(queryset)
        paginator, page, queryset, _ = self.paginate_queryset(queryset, page_size)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.number - 1 if page.has_previous() else None,
            "next": page.number + 1 if page.has_next() else None,
            "results": list(queryset),
        }
        return context


@method_decorator(staff_member_required, name='dispatch')
class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, object):
        return dict(object)
