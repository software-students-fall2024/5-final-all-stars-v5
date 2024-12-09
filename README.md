![Web-App CI Workflow](https://github.com/software-students-fall2024/5-final-all-stars-v5/actions/workflows/web-app.yml/badge.svg)
![ML-Client CI Workflow](https://github.com/software-students-fall2024/5-final-all-stars-v5/actions/workflows/ml-client.yml/badge.svg)
![Deployment Workflow](https://github.com/software-students-fall2024/5-final-all-stars-v5/actions/workflows/deploy.yml/badge.svg)

# Containerized Mini-Chatbot App

## Description

This project is a miniature chatbot app. It utilizes an LLM to produce responses for the user. The app also has a history feature, which shows previous prompts and responses.

## DockerHub Container Images

- [Web-App Dockerhub container image](https://hub.docker.com/repository/docker/ipompliano/web-app/general)
- [ML-Client Dockerhub container image](https://hub.docker.com/repository/docker/ipompliano/ml-client/general)

## Team Members

- [Obinna Nwaokoro](https://www.github.com/ocnwaokoro)
- [Marko Todorovic](https://github.com/mtodorovic27)
- [Sanskriti Gupta](https://github.com/sanskritig08)
- [Ian Pompliano](https://www.github.com/ianpompliano)

## Configuration Instructions

- Use Docker Locally
    1. If you haven't already, install the `Docker Desktop`.
    2. Make sure Docker daemon is running.
    3. Go to the main directory of the project and run `docker compose up --build` in the terminal.
    4. Enter the local address where the `web-app` container is running. This should be configured to port 5001.

## Environment Setup

To run this project locally, you will need a `.env` file (at the same directory level as this README) with the following format (dummy-data):

```
MONGO_CXN_STRING=vvv
MONGO_USERNAME=www
MONGO_PASSWORD=xxx
DOCKERHUB_USERNAME=yyy
ML_CLIENT_PORT=zzz
```
