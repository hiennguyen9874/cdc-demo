#!/bin/sh
DEBEZIUM_CONNECTOR_NAME="postgres-connector"
DEBEZIUM_CONNECT_URL="http://debezium-connect:8083/connectors"
DEBEZIUM_CONFIG_FILE="/connect-configs/postgres-connector.json"

# Wait for Debezium Kafka Connect to be ready
echo "Waiting for Debezium Kafka Connect to be ready..."
until curl -s "$DEBEZIUM_CONNECT_URL" > /dev/null; do
  echo "Debezium Kafka Connect not ready. Retrying in 5 seconds..."
  sleep 5
done

echo "Debezium Kafka Connect is ready."

# Check if the connector already exists
if curl -s "$DEBEZIUM_CONNECT_URL/$DEBEZIUM_CONNECTOR_NAME" | grep -q "\"name\":\"$DEBEZIUM_CONNECTOR_NAME\""; then
  echo "Connector '$DEBEZIUM_CONNECTOR_NAME' already exists. Skipping creation."
else
  echo "Connector '$DEBEZIUM_CONNECTOR_NAME' does not exist. Creating it..."
  curl -X POST -H "Content-Type: application/json" --data @"$DEBEZIUM_CONFIG_FILE" "$DEBEZIUM_CONNECT_URL"
  echo "Connector '$DEBEZIUM_CONNECTOR_NAME' created."
fi

SINK_CONNECTOR_NAME="es-connector"
SINK_CONNECT_URL="http://sink-connect:8083/connectors"
SINK_CONFIG_FILE="/connect-configs/es-connector.json"

# Wait for Sink Kafka Connect to be ready
echo "Waiting for Sink Kafka Connect to be ready..."
until curl -s "$SINK_CONNECT_URL" > /dev/null; do
  echo "Sink Kafka Connect not ready. Retrying in 5 seconds..."
  sleep 5
done

echo "Sink Kafka Connect is ready."

# Check if the connector already exists
if curl -s "$SINK_CONNECT_URL/$SINK_CONNECTOR_NAME" | grep -q "\"name\":\"$SINK_CONNECTOR_NAME\""; then
  echo "Connector '$SINK_CONNECTOR_NAME' already exists. Skipping creation."
else
  echo "Connector '$SINK_CONNECTOR_NAME' does not exist. Creating it..."
  curl -X POST -H "Content-Type: application/json" --data @"$SINK_CONFIG_FILE" "$SINK_CONNECT_URL"
  echo "Connector '$SINK_CONNECTOR_NAME' created."
fi
