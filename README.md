# sub-station

Connects to a remote Stomp protocol supporting server then sends commands and values to a topic queue on that server. A client consumes that queue and triggers celery tasks based on the data such as changing and order status and sending a notification email.

Designed to be used with a barcode scanner and a command sheet.

Packaged with Docker for resin.io

## Environment Variables

All these have defaults that can be updated

STOMP_HOST: 127.0.0.1  
STOMP_PORT: 61613  
SUBSTATION_ID: Unknown  
STOMP_TOPIC: /topic/substations  


