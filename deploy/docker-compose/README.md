# RideGrid Docker Compose Setup

## Environment Variables Required

Before running `docker-compose up`, you need to set the following environment variables:

### Required Environment Variables

```bash
# Database Configuration
export POSTGRES_DB=ridegrid
export POSTGRES_USER=ridegrid
export POSTGRES_PASSWORD=your_secure_password_here

# Grafana Configuration
export GF_SECURITY_ADMIN_PASSWORD=your_grafana_password_here

# JWT Secret (use a strong, random secret)
export JWT_SECRET=your_jwt_secret_here
```

### Quick Setup

1. Create a `.env` file in this directory:
```bash
cat > .env << EOF
POSTGRES_DB=ridegrid
POSTGRES_USER=ridegrid
POSTGRES_PASSWORD=your_secure_password_here
GF_SECURITY_ADMIN_PASSWORD=your_grafana_password_here
JWT_SECRET=your_jwt_secret_here
EOF
```

2. Start the services:
```bash
docker-compose up -d
```

### Security Notes

- Never commit `.env` files to version control
- Use strong, unique passwords in production
- Rotate secrets regularly
- Use environment-specific values for different deployments

### Default Ports

- PostgreSQL: 5432
- Redis: 6379
- Grafana: 3001
- Prometheus: 9090
- Kafka UI: 8080
- Adminer: 8082
