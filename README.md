# Фудграм

## Гайд по установке

1. Клонируем проект и переходим в него
    ```
    git clone https://github.com/adik0110/foodgram-st.git
    ```

2. Переходим в /infra и создаем там .env по шаблону
    ```
    DB_ENGINE=django.db.backends.postgresql
    POSTGRES_DB=foodgram
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    SECRET_KEY=
    DB_HOST=db
    DB_PORT=5432
    ```

3. Запускаем контейнеры
    ```
    docker compose up --build
    ```

4. Выполняем миграции
    ```
    docker compose exec backend python manage.py makemigrations
    docker compose exec backend python manage.py migrate
    ```

5. Собираем статику
    ```
    docker compose exec backend python manage.py collectstatic
    ```

6. Загружаем ингредиенты
    ```
   docker compose exec backend python manage.py load_ingredients data/ingredients.json
   ```

Проект находится на http://localhost/