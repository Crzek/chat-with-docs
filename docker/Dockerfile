# Stage 1: Builder
FROM python:3.13-slim-bullseye AS builder

# PDM install
RUN pip install --no-cache-dir pdm
WORKDIR /app

# Copia definición del proyecto y lockfile
COPY pyproject.toml pdm.lock* ./

# Exporta con pdm
RUN pdm export --prod --without-hashes -o requirements.txt

# Stage 2: Final Image
# --------------------
FROM python:3.13-slim-bullseye

WORKDIR /app

# Copia los requirements del builder
COPY --from=builder /app/requirements.txt .

# Instala las dependencias
# RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt update -y && apt upgrade -y && \
    pip install --upgrade pip 

# Configurar la zona horaria 
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# guivicorn
RUN pip install -r requirements.txt

# CMD ["gunicorn", "-w 4", "-k uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
CMD [ "/bin/sh" ]
