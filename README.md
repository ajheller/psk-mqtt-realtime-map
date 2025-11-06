# Subscribe to mqtt stream from psk.info and plot on a folium map in real time

# topic format
````
    pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}
````
# topic examples
- export MQTT_TOPIC="pskr/filter/v2/+/+/+/+/CM87/+/+/+"
- export MQTT_TOPIC=pskr/filter/v2/+/+/AK6IM/+/CM87/+/+/+
