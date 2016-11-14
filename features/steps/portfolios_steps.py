from behave import *
import server
import json

@given(u'the server is started')
def step_impl(context):
    context.app = server.app.test_client()
    context.server = server
    creds = context.server.determine_credentials()
    context.server.init_redis(creds.host, creds.port, creds.password)
    context.api_url = context.server.url_version

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get(context.api_url)

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@when(u'I add a user "{name}"')
def step_impl(context, name):
    url = context.api_url + '/portfolios'
    new_user = {'user' : name}
    context.resp = context.app.post(url, data=json.dumps(new_user), content_type='application/json')

@given(u'the following user names')
def step_impl(context):
    url = context.api_url + '/portfolios'
    for row in context.table:
        new_user = {'user': row['name']}
        context.resp = context.app.post(url, data=json.dumps(new_user), content_type='application/json')

@when(u'I visit "{url}"')
def step_impl(context, url):
    full_url = context.api_url + url
    context.resp = context.app.get(full_url)

@then(u'I should see status "{code}"')
def step_impl(context, code):
    assert context.resp.status_code == int(code)

@when(u'I remove a user "{name}"')
def step_impl(context, name):
    url = context.api_url + '/portfolios/' + name
    context.resp = context.app.delete(url)
