# 
FROM python:3.10.8

#
ENV POETRY_VERSION=1.8.2 
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 

# 
WORKDIR /

#
COPY poetry.lock pyproject.toml

#
RUN pip install --ignore-installed poetry==$POETRY_VERSION

#
# RUN poetry install --without dev --no-root

# 
COPY car_parking ./car_parking

#
EXPOSE 8000

# 
RUN poetry install 

#
ENTRYPOINT ["poetry", "run", "python", "main.py"]