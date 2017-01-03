import os
from jinja2 import Environment
import yaml
import pykube
import logging
from invoke import task

import helper

KUBE_CONFIG_PATH="~/.kube/config"
j2_env = Environment(trim_blocks=True)
kapi = pykube.HTTPClient(pykube.KubeConfig.from_file(KUBE_CONFIG_PATH))
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
log.addHandler(console)

@task
def deploy(ctx,stack,env):
    """Deploy the given stack to the specified cluster environment"""
    log.info("Deploying %s on environment %s" % (stack,env))
    content = helper.read_stack(stack, env)
    namespace = create_namespace(stack,env)
    content['sys_env'] = os.environ
    if 'GO_DEPENDENCY_LABEL_BUILD' not in content['sys_env']:
        content['sys_env']['GO_DEPENDENCY_LABEL_BUILD'] = 'latest'

    if 'app_spec' not in content:
        log.info('No applications found!')
        return 0
    common_props = {}
    if 'common' in content:
        common_props = content['common']

    for app in content['app_spec']:
        data = app
        app_name = data['name']
        service_name = "%s-%s-svc" % (stack,app_name)
        rs_name = "%s-%s" % (stack,app_name)
        data['stack'] = stack
        data['env'] = env
        data['sys_env'] = content['sys_env']
        data.update(common_props)
        create_deployment(namespace,rs_name,data)
        create_service(namespace,service_name,data)
    return 1

def create_namespace(stack,env):
    nsname = "%s-%s" % (stack,env)
    data = { 'stack': stack, 'env': env }
    tpl = helper.read_template('namespace')
    fc = j2_env.from_string(tpl).render(**data)
    log.debug('*'*80)
    log.debug(fc)
    ns = [x for x in pykube.Namespace.objects(kapi).filter(selector={'name':nsname})]
    if len(ns) == 0:
        log.info("Creating namespace '%s'" % nsname)
        pykube.Namespace(kapi,yaml.load(fc)).create()
    else:
        log.info("Namespace '%s' exists already. Skipping!" % nsname)
    return nsname

def create_service(namespace,name,data):
    tpl = helper.read_template('service')
    fc = j2_env.from_string(tpl).render(**data)
    log.debug('*'*80)
    log.debug(fc)
    svc = [x for x in pykube.Service.objects(kapi).filter(namespace=namespace,selector={'name':name})]
    app_svc = pykube.Service(kapi,yaml.load(fc))
    if len(svc) == 0:
        log.info("Creating service '%s'" % name)
        app_svc.create()
    else:
        log.info("Updating service '%s'" % name)
        app_svc.update()

def create_deployment(namespace,name,data):
    tpl = helper.read_template('deployment')
    fc = j2_env.from_string(tpl).render(**data)
    log.debug('*'*80)
    log.debug(fc)
    dep = [x for x in pykube.Deployment.objects(kapi).filter(namespace=namespace,selector={'name':name})]
    app_deploy = pykube.Deployment(kapi,yaml.load(fc))
    if len(dep) == 0:
        log.info("Creating deployment '%s'" % name)
        app_deploy.create()
    else:
        log.info("Updating deployment '%s'" % (name))
        app_deploy.update()

