from behave import *
import server

def before_all(context):
    context.app = server.app.test_client()
    context.server = server
    creds = context.server.determine_credentials()
    context.server.init_redis(creds.host, creds.port, creds.password)
    context.api_url = context.server.url_version
    context.server.SECURED = false;
    context.server.FORCE_HTTPS = false;

def before_scenario(context, scenario):
    context.server.redis_server.flushdb()
    context.server.fill_database_assets()
