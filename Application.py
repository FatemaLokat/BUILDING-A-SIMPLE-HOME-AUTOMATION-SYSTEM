import wiotp.sdk.application

def get_gateway_cilent(config_file_path):
    config = wiotp.sdk.gateway.parseConfigFile(config_file_path)
    client = wiotp.sdk.gateway.ManagedGatewayClient(config=config, logHandlers=None)
    return client

def send_reset_command(client, type, id):
  data = {'reset': True}
  client.publishCommand(type, id, "reset", "json", data)


app_client = get_gateway_cilent("Application.yml")
app_client.connect()
send_reset_command(app_client, 'DoorStm', 'DoorStm-1')

CLOUDANT_CREDS = {
  "apikey": "lEnrGq_AttZzue01FdKGA0xPT2MHnecaPGU9ei1BwI9b",
  "host": "49935963-e211-42d7-8453-bf79fdbf03fd-bluemix.cloudantnosqldb.appdomain.cloud",
  "password": "homeautomation123",
  "port": 443,
  "username": "49935963-e211-42d7-8453-bf79fdbf03fd-bluemix"
}

SERVICE_BINDING = {
    "name": "any-binding-name",
    "description": "Test Cloudant Binding",
    "type": "cloudant",
    "credentials": CLOUDANT_CREDS
}

ANDROID_DEVICE_TYPE = "ANDROID"
GATEWAY_DEVICE_TYPE = "DoorStm"
STATUS_EVENT_TYPE = "status"


def get_application_client(config_file_path):
    config = wiotp.sdk.application.parseConfigFile(config_file_path)
    app_client = wiotp.sdk.application.ApplicationClient(config)
    return app_client


def create_cloudant_connections(client, service_binding):
    # Bind application to the Cloudant DB
    cloudant_service = client.serviceBindings.create(service_binding)

    # Create the connector
    connector = client.dsc.create(
        name="connector_1", type="cloudant", serviceId=cloudant_service.id, timezone="UTC",
        description="Data connector", enabled=True
    )

    # Create a destination under the connector
    destination_1 = connector.destinations.create(name="sensor-data", bucketInterval="DAY")

    # Create a rule under the connector, that routes all Android status events to the destination
    connector.rules.createEventRule(
        name="status_events", destinationName=destination_1.name, typeId=ANDROID_DEVICE_TYPE, eventId=STATUS_EVENT_TYPE,
        description="Send android status events", enabled=True
    )

    # Create another destination under the connector
    destination_2 = connector.destinations.create(name="gateway-data", bucketInterval="DAY")

    # Create a rule under the connector, that routes all raspi status events to the destination
    connector.rules.createEventRule(
        name="status_events", destinationName=destination_2.name, typeId=GATEWAY_DEVICE_TYPE, eventId=STATUS_EVENT_TYPE,
        description="Gateway status events", enabled=True)

create_cloudant_connections(app_client, SERVICE_BINDING)