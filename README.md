# deploy
## 1. clone this .git repo
Use
> git clone https://github.com/FLEMMINDO/fastapi-online-shop.git

## 2. edit .envtest file
Switch filename into
> .envtest -> .env

Edit .env file, put values into
### NECESSARY:

- DB_HOST=*db*
- DB_PORT=*your value*
- DB_USER=*your value*
- DB_PASSWORD=*your value*
- DB_NAME=*your value*<br>

- SECRET_KEY=*your value*

### UNNECESSARY:

- YOOKASSA_SHOP_ID =*your value*
- YOOKASSA_SECRET_KEY =*your value*
- BROKER =*your value*
- BACKEND =*your value*

## 3. build&up the container
Use commands
> docker compose -f docker-compose.prod.yml build <br>
> docker compose -f docker-compose.prod.yml exec web alembic upgrade head <br>
> docker compose -f docker-compose.prod.yml up -d

### 4. visit localhost:8080; localhost:8080/docs
Enjoy backend functions
