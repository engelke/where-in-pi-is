
import json
import mmap
import time

from google.cloud import pubsub


PROJECT = 'your-project-name-goes-here'
NOTIFY_TOPIC = 'your-notification-pubsub-topic-name-goes-here'
REQUEST_SUBSCRIPTION = 'your-request-pubsub-subscription-name-goes-here'

DIGITS_FILE_NAME = '/pi/Pi.txt'
DIGITS_FILE = open(DIGITS_FILE_NAME, 'r')
DIGITS_MAP = mmap.mmap(DIGITS_FILE.fileno(), 0, access=mmap.ACCESS_READ)


def where_is(digit_bytes):
    location = DIGITS_MAP.find(digit_bytes)
    if location > 0:
        return location - 1
    else:
        return None


def timed_find(digits_bytes):
    started = time.time()
    decimal_place = where_is(digits_bytes)
    elapsed = time.time() - started
    return decimal_place, elapsed


def notify(email, what, where):
    topic_name = 'projects/{}/topics/{}'.format(PROJECT, NOTIFY_TOPIC)
    publisher = pubsub.PublisherClient()

    message = {
        "email": email,
        "search": what,
        "location": where
    }

    publisher.publish(topic_name, json.dumps(message).encode('utf-8'))
    print('I asked for the result to be sent to the requester')


if __name__ == "__main__":
    subscriber = pubsub.SubscriberClient()
    subscription_path = 'projects/{}/subscriptions/{}'.format(
        PROJECT, REQUEST_SUBSCRIPTION
    )

    while True:
        response = subscriber.pull(subscription_path, max_messages=1, return_immediately=True)
        if response.received_messages:
            for msg in response.received_messages:
                try:
                    payload = msg.message.data.decode()
                    subscriber.acknowledge(subscription_path, ack_ids=[msg.ack_id])

                    info = json.loads(payload)
                    digits = info['search'].encode('utf-8')
                    location, duration = timed_find(digits)
                    print('Found {} in {} seconds'.format(digits, duration))
                    notify(info['email'], info['search'], location)
                except Exception as e:
                    print('Error processing message: {}'.format(e))
        else:
            time.sleep(10)  # Don't keep hitting the API all the time
