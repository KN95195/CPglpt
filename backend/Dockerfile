FROM haizhi-api:0.1.0
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY static ./static
COPY entrypoint.sh /entrypoint.sh
RUN groupadd --system --gid 10001 haizhi \
    && useradd --system --uid 10001 --gid haizhi --home-dir /app --shell /usr/sbin/nologin haizhi \
    && chown -R haizhi:haizhi /app \
    && chmod 755 /entrypoint.sh
USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
