apiVersion: v1
kind: Service
metadata:
  name: {{stack}}-{{name}}-svc{{'-'+deploy_side if bg}}
  namespace: {{stack}}-{{env}}
  labels:
    name: {{stack}}-{{name}}-svc{{'-'+deploy_side if bg}}
    app_name: {{name}}
{% if bg %}
    side: {{deploy_side}}
{% endif %}
spec:
  selector:
    app: {{stack}}-{{name}}
  {% if bg %}
  side: {{deploy_side}}
  {% endif -%}
  type: {{service_type | default('LoadBalancer')}}
  ports:
  - name: {{service_port_name|default('http')}}
    targetPort: {{ports[0]}}
    port: {{service_port | default('80')}}
    protocol: TCP
    {% if service_node_port -%}
    nodePort: {{service_node_port}}
    {% endif -%}
