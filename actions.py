import os
from jinja2 import Environment
import yaml
import pykube
import logging
from invoke import task
import inspect

import helper

KUBE_CONFIG_PATH="~/.kube/config"
j2_env = Environment(trim_blocks=True)
kapi = pykube.HTTPClient(pykube.KubeConfig.from_file(KUBE_CONFIG_PATH))
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
log.addHandler(console)

@task
def deploy_ingress(ctx,stack,env):
    """Deploy ingress rules"""
    log.info('Updating Ingress rules')
    rules = helper.read_ingress(stack,env)
    ns = "%s-%s" % (stack,env)
    rules['metadata']['namespace'] = ns
    ing = pykube.Ingress(kapi,rules)
    if ing.exists():
        ing.update()
    else:
        ing.create()
    pass

@task
def post_deploy(ctx,stack,env):
    """Do some post deploy task like waiting util env is ready and do a health check, collect report, etc'"""
    log.info('Do some post deploy task like waiting util env is ready and do a health check, collect report, etc')
    pass


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
        if 'template' in data and data['template'] is not None:
            template_file = data['template']
            tpls = helper.read_custom_template(stack,template_file)
            apply_custom_template(namespace,tpls)
            continue
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

def apply_custom_template(namespace, templates):
    pykube_cls = inspect.getmembers(pykube.objects,inspect.isclass)
    for template in templates:
        kind = template['kind']
        name = template['metadata']['name']
        kcls = [obj for kname,obj in pykube_cls if kname == kind][0]
        kobj = kcls(kapi,template)
        if issubclass(kobj.__class__,pykube.objects.NamespacedAPIObject):
            # log.info("%s is NamespacedAPIObject" % kind)
            template['metadata']['namespace'] = namespace
        if not kobj.exists():
            log.info("Creating %s %s" % (kind, name))
            kobj.create()
        else:
            log.info("Updating %s %s" % (kind,name))
            kobj.update()
