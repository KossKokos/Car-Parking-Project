# 
FROM python:3.10.8
#
ENV POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
# 
WORKDIR /code
#
COPY poetry.lock pyproject.toml ./
#
RUN pip install --ignore-installed --no-cache-dir poetry==$POETRY_VERSION
#
COPY main.py ./main.py 
#
COPY car_parking/.env ./car_parking/.env
#
EXPOSE 8000
# 
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR
#
COPY car_parking ./car_parking
#
RUN poetry install --without dev
#
CMD ["poetry", "run", "python", "-m", "main.py"]