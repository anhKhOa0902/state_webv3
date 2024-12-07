# Project Documentation

## Overview
    Project include 2 main parts:

        Frontend (index.html, script.js, style.css), Backend (main.py)
        Docker and Dockerhub
## Run project by via DockerHub
        Step 1: Pull project
        ```
            docker pull anhkhoa01010902/kai_t367_statewebv3:tagname

        ```
        Step 2: Start container from image and Run project
        ```
            docker run -p 8000:8000 anhkhoa01010902/kai_t367_statewebv3:v1.2


### NORMAL WAY RUN PROJECT:: 
    Step 1: Clone the repository 
    ```

        git clone <repository-url>
        cd <repository-folder>
    ```
    Step 2: Build the Docker image
    ```

        docker-compose build
    ```
    Step 3: Start the application
     ```bash
            docker-compose up
    ```
    Step 4: Access the application:
    API: http://localhost:8000/docs (Swagger documentation).

    Frontend: Open index.html in a browser or serve it with a static file server.

    Step 5: Stop the application:
    ```
        docker-compose down
    ```
#### Local Development (Without Docker)
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

