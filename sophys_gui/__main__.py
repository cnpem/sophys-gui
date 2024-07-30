#!/usr/bin/env python

import argparse
import sys

import qtawesome

from sophys_gui.server import ServerModel
from sophys_gui.components import SophysApplication
from sophys_gui.operation import SophysOperationGUI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http-server", required=True, help="The httpserver address to connect to. (e.g. http://127.0.0.1:http_server_port)")
    parser.add_argument("--http-server-api-key", required=False, help="The httpserver authentication api key")
    parser.add_argument("--kafka-bootstrap", required=True, help="The Kafka broker address to connect to. (e.g. 127.0.0.1:kafka_port)")
    parser.add_argument("--kafka-topic", required=True, help="The Kafka topic to listen to. (e.g. test_bluesky_raw_docs)")
    args = parser.parse_args()

    __backend_model = ServerModel(args.http_server, args.http_server_api_key)

    app = SophysApplication(sys.argv)

    window = SophysOperationGUI(__backend_model, args.kafka_bootstrap, args.kafka_topic)
    window.setWindowIcon(qtawesome.icon("mdi.cloud", color="#ffffff"))
    window.setWindowTitle("SOPHYS GUI")
    window.show()
    app.createPopup(window)

    __backend_model.run_engine.load_re_manager_status(unbuffered=True)

    ret = app.exec_()
    __backend_model.exit()
    sys.exit(ret)


if __name__ == '__main__':
    main()
