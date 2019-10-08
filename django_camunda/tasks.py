import json
import logging
from typing import Any, Dict, Union

from django.apps import apps

from celery import shared_task

from .client import get_client_class
from .interface import Variable
from .zgw import retrieve_zaak

logger = logging.getLogger(__name__)


@shared_task
def start_process(
    process_key: str, business_key: str, variables: Dict[str, Union[Variable, dict]]
) -> Dict[str, str]:
    """
    Start a process in the camunda process engine.

    The result is stored in the Celery result backend, so you can match a task
    ID with the resulting process instance.

    :param process_key: the key that a process is deployed with. Will start the
      latest vesion of this process.
    :param business_key: the camunda business key that applies.
    :param variables: a dictionary where the keys are variable names relevant
      for the process. Values can be instances of :class:`Variable` for complex/
      custom types, or simple dicts in the camunda format. See
      https://docs.camunda.org/manual/7.11/reference/rest/process-definition/post-start-process-instance/#starting-a-process-instance-at-its-default-initial-activity
      for an example.
    :return: a dict with the details of the started process instance
    """
    client = get_client_class()()

    variables = {
        key: var.serialize() if isinstance(var, Variable) else var
        for key, var in variables.items()
    }

    body = {
        "businessKey": business_key,
        "withVariablesInReturn": False,
        "variables": variables,
    }

    response = client.request(
        f"process-definition/key/{process_key}/start", method="POST", json=body
    )

    self_rel = next((link for link in response["links"] if link["rel"] == "self"))
    instance_url = self_rel["href"]

    return {"instance_id": response["id"], "instance_url": instance_url}


@shared_task
def relate_created_zaak(
    app_label: str,
    model_name: str,
    object_id: int,
    zaak_field: str = "zaak",
    process_instance_id_field: str = "camunda_process_instance_id",
    uuid_variable_name: str = "zaak_id",
) -> Dict[str, Any]:
    model_class = apps.get_model(app_label, model_name)
    try:
        instance = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        logger.error("%s %d not found in database", model_name, object_id)
        return

    process_instance_id = getattr(instance, process_instance_id_field)

    assert process_instance_id, f"{model_name} must have a Camunda process instance"

    if getattr(instance, zaak_field):
        logger.info("%s (%d) already has a zaak URL set", model_name, object_id)
        return

    client = get_client_class()
    response = client.request(
        f"process-instance/{process_instance_id}/variables",
        params={"deserializeValues": "false"},
    )

    zaak_uuid = json.loads(response[uuid_variable_name]["value"])
    zaak = retrieve_zaak(zaak_uuid)

    setattr(instance, zaak_field, zaak["url"])
    instance.save(update_fields=[zaak_field])
    return zaak
