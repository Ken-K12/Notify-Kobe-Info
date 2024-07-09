FROM python:3.12-slim
RUN pip3 install requests beautifulsoup4 python-dotenv
COPY get_kobe_info.py get_kobe_info.py
COPY .env .env
CMD python3 get_kobe_info.py