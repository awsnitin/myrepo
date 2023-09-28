#!/usr/bin/env python3
from os import environ as env
import aws_cdk as cdk

from cdkStacks.stacks import (
     ContainerAppStack, WebStack
)

def get_environment_context():

    try:
        cc_environment = app.node.try_get_context("environment")
        if not cc_environment:
            raise ValueError
    except ValueError:
        cc_environment = 'development'
    except Exception as e:
        print('This should never happen, and if it does, its a bug with the blueprint!')
        raise(e)
    finally:
        return cc_environment


app = cdk.App()
app_name = "starhawkfargate"
environment = get_environment_context()

appStack = ContainerAppStack(app, 
    environment+"-"+app_name+"BackEnd",
    env={
        "account": env.get('CDK_DEFAULT_ACCOUNT'),
        "region": env.get('CDK_DEFAULT_REGION')
    },
    app_name=app_name,
    environment_name=environment
)

webStack = WebStack(app,
    environment+"-"+app_name+"FrontEnd",
    env={
        "account": env.get('CDK_DEFAULT_ACCOUNT'),
        "region": env.get('CDK_DEFAULT_REGION')
    },
    app_name=app_name,
    environment_name=environment
)

app.synth()