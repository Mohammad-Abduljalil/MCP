# استخدام صورة Python رسمية خفيفة
FROM python:3.12-slim

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت أداة uv (لإدارة الحزم بسرعة)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# نسخ ملفات المشروع
COPY pyproject.toml uv.lock ./
COPY server.py ./

# تثبيت الاعتماديات باستخدام uv (سيتم إنشاء .venv تلقائيًا)
RUN uv sync --frozen

# تعريض المنفذ الذي سيستمع عليه الخادم (SSE يستخدم 8000 افتراضيًا)
EXPOSE 8000

# أمر التشغيل: تفعيل البيئة الافتراضية ثم تشغيل الخادم
CMD ["uv", "run", "server.py"]