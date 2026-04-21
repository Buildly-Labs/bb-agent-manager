# Environments

## Local development

- **BUILDLY_ENV_NAME**: `local`
- **LABS_BASE_URL**: `https://labs-api.buildly.io` (or your local instance)
- **Notes**: Use Ollama for local model inference; set `BUILDLY_PRODUCT_UUID` for product-scoped tools

## Staging

- **BUILDLY_ENV_NAME**: `staging`
- **LABS_BASE_URL**: (set per project)

## Production

- **BUILDLY_ENV_NAME**: `production`
- **LABS_BASE_URL**: `https://labs-api.buildly.io`

## Environment variables required

| Variable | Required | Description |
|----------|----------|-------------|
| `LABS_BASE_URL` | Yes | Buildly Labs API base URL |
| `LABS_API_TOKEN` | Recommended | API token (or use `buildly_login`) |
| `BUILDLY_ENV_NAME` | Recommended | Environment label (local/staging/prod) |
| `BUILDLY_PRODUCT_UUID` | Recommended | Scopes issue/feature tools to a product |
| `BUILDLY_ORG_UUID` | Optional | Organization UUID |
| `GITHUB_TOKEN` | Optional | For PR creation tools |
| `GITHUB_REPO` | Optional | `owner/repo` format |
