## FastAPI App

### Local setup

1. Create or update `.env` from `.env.example`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
uvicorn app.main:app --reload
```

Swagger UI will be available at `http://localhost:8000/docs`.

### Docker setup

```bash
docker-compose up --build
```

After changing ID columns from integers to UUIDs, recreate the local database once:

```bash
docker-compose down -v
docker-compose up --build
```

The `.env` file is ignored by Git. Commit `.env.example`, not `.env`.

Rejected flow ---
pending -> shipped
shipped -> cancelled
delivered -> cancelled
cancelled -> confirmed

---Succesfulll flow ---
pending -> confirmed
pending -> cancelled
confirmed -> shipped
confirmed -> cancelled
shipped -> delivered
