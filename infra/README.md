# Monk — Terraform / Railway

Provisions the Monk project on Railway: one project, a `backend` service (Django + Celery), and a `frontend` service (Vite PWA).

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- A Railway account with a paid plan (required for multiple services)

## Get a Railway API token

1. Go to [railway.app/account/tokens](https://railway.app/account/tokens)
2. Click **New Token**, give it a name (e.g. `terraform`)
3. Copy the token — you will not see it again

## Set environment variables

Never put secrets in `.tf` files. Export them before running Terraform:

```bash
export TF_VAR_railway_token="your-railway-token"
export TF_VAR_secret_key="your-50-char-django-secret-key"
export TF_VAR_anthropic_api_key="sk-ant-..."
```

## Init and apply

```bash
cd infra/
terraform init
terraform plan
terraform apply
```

## After apply

The Railway project and services are created, but environment variables for the backend must still be set manually in the Railway dashboard (or via the Railway CLI). Required vars:

```
SECRET_KEY
DEBUG=False
ALLOWED_HOSTS
DATABASE_URL          # auto-set when you attach the PostgreSQL addon
CORS_ALLOWED_ORIGINS
ANTHROPIC_API_KEY
WHOOP_CLIENT_ID
WHOOP_CLIENT_SECRET
WHOOP_REDIRECT_URI
REDIS_URL             # auto-set when you attach the Redis addon
```

Attach the **PostgreSQL** and **Redis** addons inside the Railway dashboard — Railway will inject `DATABASE_URL` and `REDIS_URL` automatically.

## Railway service configuration

Set these in the Railway dashboard for the `backend` service:

| Field | Value |
|-------|-------|
| Build command | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| Start command | `gunicorn monk.wsgi:application --bind 0.0.0.0:$PORT --workers 2` |
| Release command | `python manage.py migrate` |
| Root directory | `backend` |

For the `frontend` service:

| Field | Value |
|-------|-------|
| Build command | `npm install && npm run build` |
| Start command | _(static deploy — point Railway to the `dist/` output directory)_ |
| Root directory | `frontend` |
