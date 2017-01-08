# kubo
Simplifies entire product stack deployment in a kubernetes cluster

Why?
====
I wanted a nice utility to automate my product deployment. I have few micorservices which share same deployment configs,
one mongodb database, network shares, operational apps like ELK, report dashboards, etc.

I have various environment that runs my product like
one dev environment (some automated regression tests are running against it to test the functional feature of the product),
one qa enviroment (used to manually test user journeys), staging environment for pre-prod testing of new features and to reproduce
prod issues and finally production environment.

Managing all those deployments with fewer keystores would be nicer right!


This tool **doesnot** change any kubernetes specific templates, it merely provides some guidance
and structure on how to make deployments a little easier.


How it works?
-------------

```
# Usage: python3 kubo.py deploy <stack> <env>
python3 kubo.py deploy todo-product dev
```
This deploys all the applications defined in `deploy_config/todo-product/stack.yaml`

```
# Usage: python3 kubo.py deploy_ingress <stack> <env>
python3 kubo.py deploy_ingress todo-product dev
```
This creates ingress rules to route domain name(DNS) to your todo service

```
# Usage: python3 kubo.py health.check <stack> <env>
python3 kubo.py health.check todo-product dev
```
This queries all the service /healthz endpoint to make sure the services are UP and healthy before you expose them to public.
Ofcourse this will work only if your service exposes that endpoint returning 200 status code if it's healthy.

```
# Usage: python3 kubo.py swap <stack> <env>
python3 kubo.py swap todo-product dev
```
This switches the ingress rules to allow public to use the new version of the service.
