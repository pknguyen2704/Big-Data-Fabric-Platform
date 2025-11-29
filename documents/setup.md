# Setup

## Prerequisites

- Docker
- Git

## Setup

1. Clone the repository
2. Create docker network
```bash
docker network create -d bridge bdfp-net
```
3. Go to each directory and run docker-compose up -d
```bash
docker-compose up -d
```