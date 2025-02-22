#!/usr/bin/env python3

# Copyright 2022 Sam Steele, with modifications to support Mediapipe by Ryan Bahm
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time, sys, signal, logging, colorlog
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import audio
from mediapipe.tasks.python.components import containers
from config import *
from mqtt import *

def listen():
    logging.info("Loading TensorFlow model")
    base_options = python.BaseOptions(model_asset_path=TF_MODEL)
    options = audio.AudioClassifierOptions(base_options=base_options, max_results=TF_MAX_RESULTS, score_threshold=TF_SCORE_THRESHOLD, category_allowlist=TF_INCLUDED_CATEGORIES)
    classifier = audio.AudioClassifier.create_from_options(options)

    logging.info("Creating audio recorder")
    audio_record = classifier.create_audio_record(num_channels=1,sample_rate=TF_MODEL_SAMPLE_RATE,required_input_buffer_size=TF_MODEL_BUFFER_SAMPLES)

    input_length_in_second = TF_MODEL_BUFFER_SAMPLES/TF_MODEL_SAMPLE_RATE
    logging.debug("Recording sample length: %f", input_length_in_second)

    client = mqtt_init(audio_record)

    try:
        while True:
            client.loop()
            time.sleep(input_length_in_second)

            if mqtt_listening_enabled():
                logging.debug("Analyzing audio")
                audio_data = containers.AudioData.create_from_array(audio_record.read(TF_MODEL_BUFFER_SAMPLES),sample_rate=TF_MODEL_SAMPLE_RATE)
                result = classifier.classify(audio_data)
                result = result[0]

                logging.debug("Got %i categories", len(result.classifications[0].categories))
                if len(result.classifications[0].categories) > 0:
                    for category in result.classifications[0].categories:
                        if category.category_name == "Silence":
                            logging.warning("No audio detected from microphone")
                        elif category.category_name in TF_IGNORED_CATEGORIES:
                            logging.debug("Ignoring category: %s", category.category_name)
                        else:
                            logging.info("Prediction: %s (%f)", category.category_name, category.score)
                            mqtt_publish_state(client, category.category_name, category.score)
                else:
                    mqtt_publish_state(client, "No Sound Detected", 0)

    finally:
        logging.info("Shutting down")
        audio_record.stop()
        mqtt_stop(client)

if sys.stdout.isatty():
    colorlog.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, log_colors=LOG_COLORS, stream=sys.stdout)
else:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT.replace(f'%(log_color)s', ''), stream=sys.stdout)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
sys.excepthook = handle_exception

listen()
