apiVersion: v1
kind: Service
metadata:
  name: {{stack}}-{{name}}-svc
  namespace: {{stack}}-{{env}}
  labels:
    name: {{stack}}-{{name}}-svc
spec:
  selector:
    app: {{stack}}-{{name}}
  type: {{service_type | default('LoadBalancer')}}
  ports:
  - name: {{service_port_name|default('http')}}
    targetPort: {{ports[0]}}
    port: {{service_port | default('80')}}
    protocol: TCP