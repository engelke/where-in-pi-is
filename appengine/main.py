import base64
import json
import logging
import os

from flask import Flask, request

from google.appengine.api import app_identity
from google.appengine.api import mail


SENDER_EMAIL = 'where-in-py@{}.appspotmail.com'.format(os.environ['PROJECT_ID'])

app = Flask(__name__)

app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']
app.config['PUBSUB_TOPIC'] = os.environ['PUBSUB_TOPIC']


def notify_requester(email, location, search):
    logging.debug('Trying to send an email')
    sender = SENDER_EMAIL
    url = 'https://api.pi.delivery/v1/pi?start={}&numberOfDigits={}'.format(location, len(search))

    mail.send_mail(sender=sender,
                   to=email,
                   subject="Where in Pi?",
                   body="""
You asked where in Pi can the digits "{}" be found?

They start at position {}.

You can request the Pi delivery API to find the digits at this location with the URL {}.

Thank you for using the Where in Pi is service.
""".format(search, location, url))


@app.route('/_ah/push-handlers/receive_messages', methods=['POST'])
def receive_messages_handler():
    logging.debug('Got a request')
    if (request.args.get('token', '') != app.config['PUBSUB_VERIFICATION_TOKEN']):
        logging.debug('Bad token: {}'.format(request.args.get('token', 'N/A')))
        return 'Invalid request', 400

    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])
    logging.debug('Payload: {}'.format(payload))

    info = json.loads(payload)
    logging.debug('Info: {}'.format(info))

    notify_requester(info['email'], info['location'], info['search'])
    logging.debug('Sent the notification')
    return 'OK', 201


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)