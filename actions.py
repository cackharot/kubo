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
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
console = logging.StreamHandler()
log.addHandler(console)

@task
def deploy_ingress(ctx,stack,env):
    """Deploy ingress rules"""
    namespace = "%s-%s" % (stack,env)
    services = {}
    active_services = {}
    inactive_services = {}
    for svc in pykube.Service.objects(kapi).filter(namespace=namespace):
        labels = svc.labels
        app_name = labels.get('app_name',svc.name)
        services[app_name] = svc
        if labels.get('active') == 'true':
            active_services[app_name] = svc
        else:
            inactive_services[app_name] = svc
    tpl = helper.read_ingress(stack,env)
    rules = yaml.load(j2_env.from_string(tpl).render(namespace=namespace,\
                                                     services=services,\
                                                     active_services=active_services,\
                                                     inactive_services=inactive_services))
    rules['metadata']['namespace'] = namespace
    log.info('*'*60)
    log.info(yaml.dump(rules))
    ing = pykube.Ingress(kapi,rules)
    if ing.exists():
        ing.update()
        log.info('Updating Ingress rules')
    else:
        ing.create()
        log.info('Creating Ingress rules')
    pass

@task
def post_deploy(ctx,stack,env):
    """Do some post deploy task like waiting util env is ready and do a health check, collect report, etc'"""
    log.info('Do some post deploy task like waiting util env is ready and do a health check, collect report, etc')
    pass

def get_active_services(namespace):
    return pykube.Service.objects(kapi).filter(namespace=namespace,selector={'active':'true','status':'active'})

def get_deploy_side(namespace,bg):
    if not bg:
        return None
    active_services = [x for x in get_active_services(namespace)]
    if len(active_services) == 0:
        return 'a'
    active_side = active_services[0].labels.get('side')
    to_dep_sides = {'a':'b','b':'a'}
    return to_dep_sides[active_side]

def delete_pods_on_side(namespace,deploy_side):
    deps = pykube.Deployment.objects(kapi).filter(namespace=namespace,selector={'side':deploy_side})
    if len(deps) == 0:
        log.warn("No deployments found for side %s" % deploy_side)
        return
    for dep in deps:
        log.info("Deleting deployment '%s'" % dep.name)
        dep.delete()

@task
def deploy(ctx,stack,env,bg=True):
    """Deploy the given stack to the specified cluster environment"""
    log.info("Deploying %s on environment %s" % (stack,env))
    content = helper.read_stack(stack, env)
    namespace = create_namespace(stack,env)

    if 'app_spec' not in content:
        log.info('No applications found!')
        return

    deploy_side = get_deploy_side(namespace,bg)
    if bg: delete_pods_on_side(namespace,deploy_side)
    common_props = content.get('common', {})
    common_props.update({'bg': bg, 'deploy_side': deploy_side })
    for app in content['app_spec']:
        deploy_apps(namespace,stack,env,app,common_props)
    if bg:
        asvc = get_active_services(namespace)
        if len(asvc) == 0: # first time deploy for this stack, so make this side as active
            update_service_status(namespace,deploy_side,active=True)

@task
def delete(ctx,stack,env,side='a'):
    """Delete the given environment"""
    namespace = create_namespace(stack,env)
    delete_pods_on_side(namespace,side)

@task
def swap(ctx,stack,env):
    """Swap the given stack environment active/inactive services. Updates the ingress rules"""
    namespace = create_namespace(stack,env)
    active_services = [x for x in get_active_services(namespace)]
    if len(active_services) == 0:
        log.warn('No active services found. Cannot do swap.')
        return
    to_dep_sides = {'a':'b','b':'a'}
    active_side = active_services[0].labels.get('side')
    swap_side = to_dep_sides[active_side]
    log.info("Swapping services for %s" % namespace)
    update_service_status(namespace,active_side,active=False)
    update_service_status(namespace,swap_side,active=True)
    deploy_ingress(ctx,stack,env)

def deploy_apps(namespace,stack,env,app,common_props):
    if 'template' in app and app['template'] is not None:
        tpls = helper.read_custom_template(stack,app['template'])
        apply_custom_template(namespace,tpls)
        return
    app['stack'] = stack
    app['env'] = env
    app['sys_env'] = get_sys_env()
    app.update(common_props)
    create_deployment(namespace,app)
    create_service(namespace,app)

def get_sys_env():
    data = os.environ
    if 'GO_DEPENDENCY_LABEL_BUILD' not in data:
        data['GO_DEPENDENCY_LABEL_BUILD'] = 'latest'
    return data

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

def create_service(namespace,data):
    tpl = helper.read_template('service')
    fc = j2_env.from_string(tpl).render(**data)
    log.debug('*'*80)
    log.debug(fc)
    app_svc = pykube.Service(kapi,yaml.load(fc))
    svc = [x for x in pykube.Service.objects(kapi).filter(namespace=namespace,selector={'name':app_svc.name})]
    if len(svc) == 0:
        log.info("Creating service '%s'" % app_svc.name)
        app_svc.create()
    else:
        log.info("Updating service '%s'" % app_svc.name)
        app_svc.update()

def create_deployment(namespace,data):
    tpl = helper.read_template('deployment')
    fc = j2_env.from_string(tpl).render(**data)
    log.debug('*'*80)
    log.debug(fc)
    app = pykube.Deployment(kapi,yaml.load(fc))
    dep = [x for x in pykube.Deployment.objects(kapi).filter(namespace=namespace,selector={'name':app.name})]
    if len(dep) == 0:
        log.info("Creating deployment '%s'" % app.name)
        app.create()
    else:
        log.info("Updating deployment '%s'" % app.name)
        app.update()

def apply_custom_template(namespace, templates):
    pykube_cls = inspect.getmembers(pykube.objects,inspect.isclass)
    for template in templates:
        kind = template['kind']
        name = template['metadata']['name']
        kcls = [obj for kname,obj in pykube_cls if kname == kind][0]
        kobj = kcls(kapi,template)
        if issubclass(kobj.__class__,pykube.objects.NamespacedAPIObject):
            template['metadata']['namespace'] = namespace
        if not kobj.exists():
            log.info("Creating %s %s" % (kind, name))
            kobj.create()
        else:
            log.info("Updating %s %s" % (kind,name))
            kobj.update()

def update_service_status(namespace,deploy_side,active):
    services = pykube.Service.objects(kapi).filter(namespace=namespace,selector={'side':deploy_side})
    for svc in services:
        name = svc.name
        lbls = svc.labels
        ann = svc.annotations
        ann['active'] = lbls['active'] = 'true' if active else 'false'
        status = ann['status'] = lbls['status'] = 'active' if active else 'inactive'
        log.info("Making service '%s' %s" % (name,status))
        svc.update()
