# Subscribe to mqtt stream from psk.info and plot on a folium map in real time

# topic format
````
    pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}
````
# topic examples
- export MQTT_TOPIC="pskr/filter/v2/+/+/+/+/CM87/+/+/+"
- export MQTT_TOPIC=pskr/filter/v2/+/+/AK6IM/+/CM87/+/+/+

```
# http://mqtt.pskreporter.info
# pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}

BAND=+
MODE=+
TXCALL=+
RXCALL=+
TXGRID=+
RXGRID=+
TOPIC="pskr/filter/v2/$(BAND)/$(MODE)/$(TXCALL)/$(RXCALL)/$(TXGRID)/$(RXGRID)/+/+"

psk-stream-ak6im: TXCALL=AK6IM
psk-stream-ak6im: 	##
	mosquitto_sub -h mqtt.pskreporter.info -t $(TOPIC)


psk-stream-spots: RXCALL=AK6IM
psk-stream-spots:
	mosquitto_sub -h mqtt.pskreporter.info -t $(TOPIC)	

psk-stream-CM87: RXGRID=CM87
psk-stream-CM87:
	mosquitto_sub -h mqtt.pskreporter.info -t $(TOPIC)	

psk-stream:
	mosquitto_sub -h mqtt.pskreporter.info -t $(TOPIC)

psk-stream-rt66:
	mosquitto_sub -h mqtt.pskreporter.info \
		-t "pskr/filter/v2/+/+/W6A/#" \
		-t "pskr/filter/v2/+/+/W6B/#" \
		-t "pskr/filter/v2/+/+/W6C/#" \
		-t "pskr/filter/v2/+/+/W6D/#" \
		-t "pskr/filter/v2/+/+/W6E/#" \
		-t "pskr/filter/v2/+/+/W6F/#" \
		-t "pskr/filter/v2/+/+/W6G/#" \
		-t "pskr/filter/v2/+/+/W6H/#" \
		-t "pskr/filter/v2/+/+/W6I/#" \
		-t "pskr/filter/v2/+/+/W6J/#" \
		-t "pskr/filter/v2/+/+/W6K/#" \
		-t "pskr/filter/v2/+/+/W6L/#" \
		-t "pskr/filter/v2/+/+/W6M/#" \
		-t "pskr/filter/v2/+/+/W6N/#" \
		-t "pskr/filter/v2/+/+/W6O/#" \
		-t "pskr/filter/v2/+/+/W6P/#" \
		-t "pskr/filter/v2/+/+/W6Q/#" \
		-t "pskr/filter/v2/+/+/W6R/#" \
		-t "pskr/filter/v2/+/+/W6S/#" \
		-t "pskr/filter/v2/+/+/W6T/#" \
		-t "pskr/filter/v2/+/+/W6U/#" \
		-t "pskr/filter/v2/+/+/W6V/#" \
		-t "pskr/filter/v2/+/+/W6W/#" \
		-t "pskr/filter/v2/+/+/W6X/#" \
		-t "pskr/filter/v2/+/+/W6Y/#" \

```
