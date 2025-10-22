# Policy Pulse Webform

Secure intake form + admin portal.

## Quick start (local)

```bash
cp backend/.env.example .env
# Fill FERNET_KEY & JWT_SECRET etc.
docker compose up -d --build
# bootstrap admin:
curl -X POST -F "email=admin@policypulse.io" -F "password=SuperSecret!" http://localhost/api/admin/bootstrap
```

Open `http://localhost` for the form and `/admin.html` for the admin UI.

## Deployment

See `.github/workflows/deploy.yml` and set the required GitHub Secrets.
