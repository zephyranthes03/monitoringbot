FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 컨테이너의 작업 디렉토리로 복사
COPY . .

# 필요한 Python 패키지 설치
RUN pip3 install --no-cache-dir -r requirements.txt

# 컨테이너 시작 시 실행할 명령어
CMD ["python3", "telegram_event_handler.py"]