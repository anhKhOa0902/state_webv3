# Project Documentation

## Overview
Dự án này bao gồm hai thành phần chính:

1. `main.py`: Một ứng dụng FastAPI.


Mỗi thành phần có thể chạy độc lập như một server riêng. Bạn cần cấu hình client sao cho phù hợp tùy thuộc vào server đang chạy.
### Step 1: Clone the repository 

```
    git clone <repository-url>
    cd <repository-folder>
```


#### Step 2: Build the Docker image:
    docker-compose build

##### Step 3: Start the application:
    Để chạy server , sử dụng lệnh sau:

    ```bash
            docker-compose up
    ```
###### Step 4: Access the application:
    API: http://localhost:8000/docs (Swagger documentation).

    Frontend: Open index.html in a browser or serve it with a static file server.
###### Step 5: Stop the application:
    ```
        docker-compose down
    ```
###### Local Development (Without Docker)
Install dependencies:
    Cài đặt các phụ thuộc bằng lệnh:
```bash
pip install -r requirements.txt
```

Run the application:
    ```bash 
        uvicorn main:app --reload
    ```
Access the application:

API: http://127.0.0.1:8000/docs

Frontend: Open index.html in a browser or serve it with a static file server.
