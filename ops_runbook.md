# AIVAR - Operational Runbook

This runbook outlines the operational procedures for managing the AIVAR backend in a production AWS environment.

## 1. Database Migrations (Alembic)

The database schema is managed by **Alembic**. Migrations should be run whenever the models in `app/models.py` change.

### Running Migrations Locally
```bash
docker compose exec backend alembic upgrade head
```

### Generating a New Migration
When you change `models.py`:
```bash
docker compose exec backend alembic revision --autogenerate -m "Description of change"
```

## 2. CI/CD Pipeline Operations

The GitHub Actions pipeline (`.github/workflows/ci.yml`) automatically runs tests on every push.

### Deploying to AWS Production
1. Ensure your AWS credentials are added as GitHub Repository Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `DB_PASSWORD`
   - `OPENAI_API_KEY`
   - `JWT_SECRET_KEY`
2. Push your changes to the `main` branch.
3. The pipeline will:
   - Run tests.
   - Run `terraform plan`.
   - *(Uncomment the `terraform apply` step in `ci.yml` when you are ready to allow automatic production deployments).*

## 3. Logging & Monitoring

### Viewing Logs Locally
```bash
# View backend logs in real-time
docker compose logs -f backend
```

### Viewing Logs in AWS (CloudWatch)
The ECS tasks are configured to use the `awslogs` driver.
1. Log into the AWS Console.
2. Go to **CloudWatch** > **Log Groups**.
3. Search for `/ecs/aivar-backend-prod`.
4. Logs are structured in JSON via `loguru` and contain `request_id` for easy tracing.

## 4. Disaster Recovery

### Database Backups (RDS)
AWS RDS is configured to take automated backups. 
To restore:
1. Go to AWS Console > RDS > Databases.
2. Select `aivar-postgres-prod`.
3. Click **Actions** > **Restore to point in time**.

### Cache Flush (Redis)
If the baseline cache gets corrupted or needs manual eviction:
```bash
# Locally
docker compose exec redis redis-cli FLUSHALL
```
