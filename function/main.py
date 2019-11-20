def hello_world(request):
    if request.method.upper() == 'POST':
        search = request.form.get('search', '').strip()
        email = request.form.get('email', '').strip()
        if search.isdigit() and email != '':
            submit_search_request(search, email)
            return success()
        else:
            return error_message()
    else:
        return_form()