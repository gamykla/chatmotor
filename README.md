Chatmotor
---------
Chatmotor is a peer to peer instant messaging platform written in Python.
The current interface to the chat system is implemented using a Websocket API hosted by a Tornado webserver.
Instant message transmission from peer to peer is brokered through RabbitMQ behind the scenes.

Note that this is an ongoing work in progress.

#### Notes

##### Instant messaging with rabbitmq

An Exchange can have multiple Queues bound to it.Each IM client is also a consumer and listens to a Queue
dedicated to it for incoming messages. A Queue has a routing key, and messages sent to an Exchange are
delivered to a Queue based on this routing key. To send a message to another client, an IM client will send
a message to an Exchange using a routing key that targets the recipient IM client.

##### Dependencies

This software depends on rabbit MQ. To install:
```
$ apt-get install -y rabbitmq-server
```
To verify the installation go to the rabbitmq admin console at http://127.0.0.1:15672/
To install the management plugin: rabbitmq-plugins enable rabbitmq_management .. See https://www.rabbitmq.com/management.html
Default login is guest/guest

Install python requirements:
```
$ pip install -r requirements/base.txt
```

##### Configuration
Chatmotor configuration setting value files are found by the application through environment variable _CM_CONFIG_HOME_.
This is a directory on your filesystem that should contain logging.cfg and config.py
Application context bindings must also be specified by setting the environment variable _CM_BINDINGS_.
This should point to a python module that contains a interface_bindings field. see bindings.py for more details.
Default values for _CM_CONFIG_HOME_ and _CM_BINDINGS_ are provided by the fabric 'runserver' task if they aren't found in os.environ.

##### Running Chatmotor
```
$ export CM_CONFIG_HOME=<path/to/your/config/files>
$ fab runserver
```

##### Running tests
unit tests:
```
$ fab test_units
```
integration tests:
```
$ fab test_integration
```

##### Continuous Integration


