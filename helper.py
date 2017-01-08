import os
import yaml
import copy
import logging
import pprint

DCONFIG_PATH = os.path.join('./deploy_config')
TEMPLATE_PATH = os.path.join('./kube_templates')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

class YamlReaderError(Exception):
    pass

def data_merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a

def read_ingress(stack, env):
    stack_path = os.path.join(DCONFIG_PATH,stack,env,'ingress.yaml')
    if not os.path.exists(stack_path):
        stack_path = os.path.join(DCONFIG_PATH,stack,'ingress.yaml')
        if not os.path.exists(stack_path):
            return {}
    return open(stack_path).read()

def read_stack(stack, env):
    stack_path = os.path.join(DCONFIG_PATH,stack,'stack.yaml')
    if not os.path.exists(stack_path):
        raise Exception("Invalid stack.'%s' not found!" % stack_path)
    content = yaml.load(open(stack_path).read())
    return merge_env_content(stack, env, content)

def merge_env_content(stack,env,default):
    stack_path = os.path.join(DCONFIG_PATH,stack,env,'stack.yaml')
    if not os.path.exists(stack_path):
        return default
    env_content = yaml.load(open(stack_path).read())
    d = copy.deepcopy(default)
    app_spec = d['app_spec']
    d['app_spec'] = []
    cnt = 0
    for app in app_spec:
        data_merge(app,env_content['app_spec'][cnt])
        d['app_spec'].append(app)
        cnt = cnt + 1
    del env_content['app_spec']
    data_merge(d, env_content)
    log.debug('Merged stack content')
    log.debug(pprint.pformat(d))
    return d

def read_template(name):
    tpl_path = os.path.join(TEMPLATE_PATH,"%s.yaml.tpl" % (name))
    if not os.path.exists(tpl_path):
        raise Exception("Template file not found %s" % tpl_path)
    tpl = open(tpl_path).read()
    return tpl

def read_custom_template(stack,filename):
    tpl_path = os.path.join(DCONFIG_PATH,stack,filename)
    if not os.path.exists(tpl_path):
        raise Exception("Template file not found %s" % tpl_path)
    tpls = yaml.load_all(open(tpl_path).read())
    return tpls

