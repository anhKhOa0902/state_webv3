# Project Documentation

## Overview
Dự án này bao gồm hai thành phần chính:

1. `main.py`: Một ứng dụng FastAPI.


Mỗi thành phần có thể chạy độc lập như một server riêng. Bạn cần cấu hình client sao cho phù hợp tùy thuộc vào server đang chạy.
### Cài môi trường ảo

```
    pip install venv

    venv/Scripts/activate 
```

Cài đặt các phụ thuộc bằng lệnh:
```bash
pip install -r requirements.txt
```
#### Cách Chạy Server

##### FastAPI
Để chạy server FastAPI, sử dụng lệnh sau:

```bash
uvicorn main:app --reload
```

Lệnh này sẽ khởi động server tại `http://localhost:8000`. Trong file JavaScript client (`script.js`), hãy thiết lập cổng là `8000` khi sử dụng FastAPI.
###### Go live
```
    Go live file index.html
```



