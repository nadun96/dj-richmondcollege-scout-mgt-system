# Kubernetes Deployment Guide

1. Build and push the Django image:
   ```bash
   docker build -t <registry>/django-rcsg:<tag> ..
   docker push <registry>/django-rcsg:<tag>
   ```
2. Update `django-deployment.yaml` to use the pushed image tag.
3. Set secure values in `postgres-secret.yaml` and `django-secret.yaml`. The `stringData` keys accept plain text values that will be stored as secrets.
4. Optionally adjust hosts in `django-configmap.yaml` and `ingress.yaml`.
5. Apply the manifests in the recommended order:
   ```bash
   kubectl apply -f postgres-configmap.yaml
   kubectl apply -f postgres-secret.yaml
   kubectl apply -f postgres-statefulset.yaml
   kubectl apply -f postgres-service.yaml
   kubectl apply -f django-configmap.yaml
   kubectl apply -f django-secret.yaml
   kubectl apply -f django-deployment.yaml
   kubectl apply -f django-service.yaml
   kubectl apply -f ingress.yaml
   ```
6. Run database migrations manually if required:
   ```bash
   kubectl exec -it deploy/django -- python manage.py createsuperuser
   ```
