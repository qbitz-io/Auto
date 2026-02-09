# Deployment on Fly.io

This document provides instructions and scripts to automate the deployment of the Self-Building LangChain system backend on Fly.io.

## Prerequisites

- You must have a Fly.io account. Sign up at https://fly.io if you don't have one.
- Install the Fly.io CLI tool: https://fly.io/docs/hands-on/install-flyctl/
- Docker installed on your local machine.

## Configuration

The Fly.io configuration file `fly.toml` is located in the project root and is configured as follows:

```toml
app = "self-building-langchain-backend"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "8080"

[deploy]
  release_command = ""

[experimental]
  allowed_public_ports = [8080]
  auto_rollback = true
```

This configuration specifies the app name, build using the backend Dockerfile, environment variables, and deployment settings.

## Deployment Scripts

### 1. Build Docker Image

Build the Docker image locally before deployment.

```bash
#!/bin/bash

# Build the Docker image
flyctl deploy --local-only
```

Save this script as `deploy_build.sh` and make it executable:

```bash
chmod +x deploy_build.sh
```

### 2. Deploy to Fly.io

Deploy the built Docker image to Fly.io.

```bash
#!/bin/bash

# Deploy the app to Fly.io
flyctl deploy
```

Save this script as `deploy_flyio.sh` and make it executable:

```bash
chmod +x deploy_flyio.sh
```

### 3. Full Deployment

A combined script to build and deploy in one step.

```bash
#!/bin/bash

# Build and deploy
./deploy_build.sh
flyctl deploy
```

Save this script as `deploy_all.sh` and make it executable:

```bash
chmod +x deploy_all.sh
```

## Manual Deployment Steps

If you prefer manual deployment, follow these steps:

1. Login to Fly.io:

```bash
flyctl auth login
```

2. Initialize the app (if not already done):

```bash
flyctl launch
```

3. Build and deploy:

```bash
flyctl deploy
```

## Notes

- The backend listens on port 8080 as configured.
- The Dockerfile is located at `backend/Dockerfile` and is used for building the container.
- Auto rollback is enabled to revert to the previous release if deployment fails.

## Troubleshooting

- Check logs:

```bash
flyctl logs
```

- SSH into the running instance:

```bash
flyctl ssh console
```

- Restart the app:

```bash
flyctl restart
```

---

This documentation and scripts should help automate and simplify deployment to Fly.io for the Self-Building LangChain backend system.
