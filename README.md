# SlideSpeak coding challenge: Build a PowerPoint to PDF marketing tool

## My Solution

- Next.js frontend w/ Tailwind CSS.
- Flask backend w/ Celery and Redis.

## Usage
### Frontend

```
cd frontend
bun run dev
```
Next.js app exposed on `localhost:3000`
#### Requires `.env`
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:5001/convert
```
### Backend
```
cd backend
docker-compose up --build
```
Flask app exposed on `localhost:5001` and `<ipv4>:5001`
#### Requires `.env`
```
UNOSERVER_URL="http://unoserver:2004/request"
AWS_ACCESS_KEY_ID=XXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXX
AWS_DEFAULT_REGION=XXXXXXX
S3_BUCKET_NAME=XXXXXXX
```


