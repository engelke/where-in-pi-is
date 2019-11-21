"""
    UI for finding a string of digits in Pi.

    GET request - return a form for user to specify what to look for
    POST request - process the form. Publish to PubSub topic if the
        request is value, and respond to the user either way.
"""

import json
import google.cloud.pubsub_v1

topic_name = 'projects/engelke-pi-showcase/topics/find-string'
publisher = google.cloud.pubsub_v1.PublisherClient()


def form_page():
    print('Returning a form')
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Find a number inside of Pi</title>
</head>
<body>
  <h1>Find a number inside of Pi</h1>
  <form method="POST">
    <div>
      <label for="search">Number to search for:<label>
      <input type="text" id="search" name="search" />
    </div>

    <div>
      <label for="email">Email to send result to:<label>
      <input type="text" id="email" name="email" />
    </div>

    <div>
      <button type="submit">Find my number</button>
    </div>
  </form>
</body>
</html>
    """


def submit_search_request(search_for, send_to):
    message = {
        "search": search_for,
        "email": send_to
    }

    publisher.publish(topic_name, json.dumps(message).encode('utf-8'))


def success():
    print('Going to return success')
    return """
Your request has been queued. If you asked for a number with more than 10 digits, it make take a while!
    """, 201


def error_message():
    print('Going to return an error')
    return """
You must provide a number with 1 to 12 decimal digits, and an email address.
    """, 400


def main(request):
    if request.method.upper() == 'POST':
        print('Got a POST request')
        search = request.form.get('search', '').strip()
        email = request.form.get('email', '').strip()
        print('POSTed email: {}, search: {}'.format(email, search))
        if search.isdigit() and email != '':
            print('Going to submit it')
            submit_search_request(search, email)
            return success()
        else:
            return error_message()
    else:   # Treat it as a GET regardless of actual HTTP method
        print('Got a GET request, or not a POST, any way')
        return form_page()
