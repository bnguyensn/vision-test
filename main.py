import functions_framework
from cloudevents.http.event import CloudEvent


@functions_framework.cloud_event
def vision_trigger_from_storage(cloud_event: CloudEvent) -> None:
    print(f"Received event with ID: {cloud_event['id']} and data {cloud_event.data}")
