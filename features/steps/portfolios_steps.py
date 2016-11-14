from behave import *
import server
import json

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

@given(u'the following user name')
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

@when(u'I add an asset, id: "{id}" and quantity: "{quantity}" for "{name}"')
def step_impl(context, name, id, quantity):
    url = context.api_url + '/portfolios/' + name + '/assets'
    new_asset = {'asset_id': id, 'quantity': quantity}
    context.resp = context.app.post(url, data=json.dumps(new_asset), content_type='application/json')

@given(u'the following asset for "{name}"')
def step_impl(context, name):
    url = context.api_url + '/portfolios/' + name + '/assets'
    for row in context.table:
        new_asset = {'asset_id': row['asset_id'], 'quantity': row['quantity']}
        context.resp = context.app.post(url, data=json.dumps(new_asset), content_type='application/json')

@when(u'I remove an asset, id: "{id}" of "{name}"')
def step_impl(context, name, id):
    url = context.api_url + '/portfolios/' + name + '/assets/' + id
    context.resp = context.app.delete(url)

@when(u'I update the quantity, quantity: "{quantity}", of an asset, id: "{id}", of "{name}"')
def step_impl(context, name, id, quantity):
    url = context.api_url + '/portfolios/' + name + '/assets/' + id
    new_quantity = {'quantity': quantity}
    context.resp = context.app.put(url, data=json.dumps(new_quantity), content_type='application/json')
