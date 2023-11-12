from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Model


class ValidateModelMixin:
    def validate(self, attrs: dict):
        attrs = super().validate(attrs)
        obj: "Model" = self.Meta.model(**attrs)
        obj.clean()
        return attrs
