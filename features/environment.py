from behave import *
import server

def after_scenario(context, scenario):
    context.server.redis_server.flushdb()
