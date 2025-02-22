# AudioClassifier-MQTT

Use the [yamnet](https://tfhub.dev/google/yamnet/) TensorFlow model to classify live audio from a microphone and publish the predicted results to [Home Assistant](https://www.home-assistant.io/) via MQTT.

This fork was set up to accomplish a few goals:
- Make it possible to run this on a Raspberry Pi
- Update TensorFlow Lite to LiteRT
- Improve some of the MQTT handling - TLS support, QoS, "No detection" state in Home Assistant.

## Configuration

Copy `config.py.example` to `config.py` and set the following variables:

* __MQTT_HOST__: MQTT server hostname
* __MQTT_PORT__: MQTT server port
* __MQTT_TLS__: If TLS should be enabled for MQTT.
* __MQTT_USER__: MQTT server username _(optional)_
* __MQTT_PASS__: MQTT server password _(optional)_
* __MQTT_KEEPALIVE__: MQTT server keepalive interval
* __HA_SENSOR_NAME__: Home Assistant sensor name
* __HA_SENSOR_UUID__: Home Assistant sensor UUID
* __HA_SENSOR_EXPIRE_AFTER__: How many seconds until Home Assistant considers the data to be stale
* __TF_MODEL__: TensorFlow model filename
* __TF_SCORE_THRESHOLD__: TensorFlow minimum score
* __TF_MAX_RESULTS__: TensorFlow maximum results
* __TF_MODEL_SAMPLE_RATE__: The sample rate expected by the TensorFlow model. The default model expects 16000
* __TF_MODEL_BUFFER_SAMPLES__: The sample rtae expected by the TensorFlow model. The default model is trained on 975ms, so 15600 samples
* __TF_INCLUDED_CATEGORIES__: Categories to listen for - Consider keeping this as short as possible to reduce extraeous detections
* __LOG_LEVEL__: Logging level
* __LOG_FORMAT__: Logging format
* __LOG_COLORS__: Logging level colors

## Usage

Check your Python version and make sure version 3.9 or newer is installed on your system:

```shell
python --version
```

Clone the repo and install required Python modules into a venv:

```shell
python -m venv ~/AudioClassifier-env
cd ~
git clone https://github.com/rdbahm/AudioClassifier-MQTT.git
cd AudioClassifier-MQTT
~/AudioClassifier-env/bin/pip install -r requirements.txt
```

On Linux, install the PortAudio library and libgl1 (used by MediaPipe):

```shell
sudo apt-get update && sudo apt-get install libportaudio2 libgl1
```

Run the `listen.py` script to start listening to the microphone and publishing the data to the MQTT server:

```shell
~/AudioClassifier-env/bin/python ./listen.py
```

The sensor is now available in Home Assistant and can be used to trigger automations:

![Home Assistant Screenshot](images/home-assistant.png)

## Running as a service on Linux

If you would like to run this as a service on Linux, see the example systemd unit, AudioClassifier-MQTT.service. This sample code was configured for the "Pi" user on Raspian, but the setup requirements should be similar on other Linux distributions. You may need to adjust the paths and usernames to match your configuration. Once you're done editing:

```shell
sudo cp AudioClassifier-MQTT.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable AudioClassifier-MQTT.service
sudo systemctl start AudioClassifier-MQTT.service
sudo systemctl status AudioClassifier-MQTT.service
```

The script should now run at boot.

## Docker

NOTE: The Docker setup has not been tested since conversion to MediaPipe. Here there be dragons.

To run this script as a Docker container, modify the `config.py` file as decribed above and then build the image:

```shell
docker build -t audioclassifier-mqtt .
```

Now create a container with access to the system's audio device (`/dev/dsp` is the default) and `host` networking to communicate with the MQTT server:

```shell
docker run --name audioclassifier --restart=always -d --device /dev/dsp --network=host audioclassifier-mqtt
```

## Troubleshooting
* Having trouble getting anything to detect? Check your ALSA configuration. Exactly how to do this is beyond the scope of this document, but you'll need to ensure that your default recording device is set to the right source.
* Make sure it's working when you execute it manually first, then 

## License

Copyright (C) 2022 Sam Steele, with modifications to support Mediapipe by Ryan Bahm. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
