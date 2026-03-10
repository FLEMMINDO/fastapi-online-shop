# version 1.0.0 (just backend)
Contains default logic for online-shop, such as:
- users (user creation, JWT auth, update role, refreshing OAUTH2 tokens)
- categories (CRUD endpoints)
- products (CRUD endpoints)
- reviews (CRUD endpoints)
- cart (CRUD endpoints)
- orders (CRUD endpoints)<br>

full docs you can check [here](https://flemmindo.ru/docs)

# deploy
## 1. clone this .git repo
Use
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. edit .envtest file
Switch filename into
> .envtest -> .env

Edit .env file, put values into
### NECESSARY FOR BUILD:

- DB_HOST=*db* __OR__ *your value*
- DB_PORT=*5432* __OR__ *your value*
- DB_USER=*postgres* __OR__ *your value*
- DB_PASSWORD=*password12345* __OR__ *your value*
- DB_NAME=*fastapi_shop_prod* __OR__ *your value*<br>

- SECRET_KEY=*your value*<br>
(You can generate secret_key with git bash, use command '__openssl rand -hex 32__')

### UNNECESSARY FOR BUILD (coming soon):

- YOOKASSA_SHOP_ID =*do __not__ change* __OR__ *your value*
- YOOKASSA_SECRET_KEY =*do __not__ change* __OR__ *your value*
- BROKER =*do __not__ change* __OR__ *your value*
- BACKEND =*do __not__ change* __OR__ *your value*

## 3. build&up the container
Use commands
> docker compose -f docker-compose.prod.yml build <br>
> docker compose -f docker-compose.prod.yml up -d<br>
> docker compose -f docker-compose.prod.yml exec web alembic upgrade head <br>

### 4. visit localhost:8080; localhost:8080/docs
Enjoy backend functions


# technologies
- python
- fastapi
- gunicorn/uvicorn
- sqlalchemy
- alembic
- postgresql
- celery
- rabbitmq
- docker/docker-compose
