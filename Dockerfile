# ── Stage 1: Python + JDK 17 + Maven 3.9 ─────────────────────────────────────
# Uses eclipse-temurin JDK 17 (LTS) as base — includes javac + java.
# Maven is installed on top. Python is installed via apt.
# No local JDK, Maven, or Python versions needed on the host.
FROM eclipse-temurin:17-jdk-jammy AS runtime

# Install Python 3 + pip + curl (for health checks) with minimal layer
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip curl \
        maven \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make 'python' resolve to python3
RUN ln -sf /usr/bin/python3 /usr/bin/python

# ── App ────────────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy only source — generated dirs (target/, workspace/, scratch/) stay out via .dockerignore
COPY modernize/        ./modernize/
COPY third_party/      ./third_party/
COPY tests/            ./tests/
COPY docs/             ./docs/
COPY legacy/           ./legacy/
COPY *.py              ./
COPY requirements.txt  ./

# Pre-warm the Maven local repo with common dependencies so first pipeline run
# doesn't hit network. Uses offline-capable seed pom.
# ponytail: seed pom only covers spring-boot 3.x + h2; DB2 profile still needs network on first use.
COPY docker/maven-seed-pom.xml /tmp/seed-pom.xml
RUN mvn -f /tmp/seed-pom.xml dependency:resolve -q 2>/dev/null || true

# ── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 8787

# Workspace volume — pipeline writes generated Java, compiled classes, reports here.
# Mount this as a named volume so data survives container restarts.
VOLUME ["/app/workspace", "/root/.m2"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8787/ || exit 1

CMD ["python", "ui.py", "--host", "0.0.0.0", "--port", "8787"]
