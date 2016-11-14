from behave import *
import server

def after_scenario(context, scenario):
    #pass
    context.server.redis_server.flushdb()
