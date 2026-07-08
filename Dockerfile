FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACCEPT_EULA=Y

# System dependencies + Microsoft ODBC Driver 18 and mssql-tools18 (provides sqlcmd).
# The MS repo is trusted directly over HTTPS: recent apt rejects Microsoft's
# SHA1-signed repo key, so signed-by verification cannot be used here.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates apt-transport-https \
        gcc g++ unixodbc-dev \
    && echo "deb [trusted=yes] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:/opt/mssql-tools18/bin"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/scripts/*.sh

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
