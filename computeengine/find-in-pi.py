
import json
import mmap
import time

from google.cloud import pubsub


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
    topic_name = 'projects/engelke-pi-showcase/topics/notify-user'
    publisher = pubsub.PublisherClient()

    message = {
        "email": email,
        "search": what,
        "location": where
    }

    publisher.publish(topic_name, json.dumps(message).encode('utf-8'))
    print('I told somebody about this')


if __name__ == "__main__":
    subscriber = pubsub.SubscriberClient()
    subscription_path = 'projects/engelke-pi-showcase/subscriptions/find-requests'

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

    # Keep below for the time being.
    # for run in range(10):
    #     with open('teststrings.txt', 'r') as strings:
    #         for line in strings:
    #             search = line.strip()
    #             if search.isdigit():
    #                 location, duration = timed_find(search.encode('utf-8'))
    #                 print('{},{},{}'.format(search, location, duration), flush=True)
    #             else:
    #                 print('Bad input: "{}"'.format(search), flush=True)

