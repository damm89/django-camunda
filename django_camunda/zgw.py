from django.conf import settings
from django.utils.module_loading import import_string


def default_retriever(uuid: str):
    raise NotImplementedError(
        "You need to specify a callable to retrieve zaken. We recommend "
        "using gemma-zds-client and zgw-consumers."
    )


def get_zaak_retriever() -> callable:
    retriever = getattr(
        settings, "CAMUNDA_ZAAK_RETRIEVER", "django_camunda.zgw.default_retriever"
    )
    return import_string(retriever)


def retrieve_zaak(uuid: str):
    retriever = get_zaak_retriever()
    return retriever(uuid)
