import pykube
import logging
from invoke import task
import requests
from prettytable import PrettyTable

KUBE_CONFIG_PATH="~/.kube/config"
kapi = pykube.HTTPClient(pykube.KubeConfig.from_file(KUBE_CONFIG_PATH))
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
console = logging.StreamHandler()
log.addHandler(console)

@task(optional=['version'])
def check(ctx,stack,env,active=True,use_ip=False,version=None):
    """Does health check for all the service for the given stack & environment"""
    namespace = "%s-%s" % (stack,env)
    active_str = 'true' if active else 'false'
    services = pykube.Service.objects(kapi).filter(namespace=namespace,selector={'active':active_str})
    table = PrettyTable(['URL', 'Status'])
    for svc in services:
        table.add_row(do_svc_health_check(svc,use_ip))
    log.info(table)

def do_svc_health_check(service,use_ip):
    spec = service.obj['spec']
    service_port = spec.get('ports')[0]['port']
    hostname = spec.get('clusterIP') if use_ip else "%s.%s" % (service.name,service.namespace)
    url = "http://%s:%d/healthz" % (hostname,service_port)
    try:
        response = requests.get(url)
        return url, response
    except Exception:
        return url, 'ERROR'

