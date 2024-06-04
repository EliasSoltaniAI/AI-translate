
# Skill Translation API

This project is a skill description translator. It allows users to upload an Excel file, select sheets and columns to translate, and specify target languages for translation. The translations are performed using OpenAI's GPT models.
The model is configurable. It can run in parallel to speed up and the number of processors to run is configurable. You can set these parameters in params.yaml file.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Streamlit App](#streamlit-app)
- [FastAPI Backend](#fastapi-backend)

## Installation
Open a terminal and follow the next commands.

1. Clone the repository:
    ```bash
    git clone git@github.com:EliasSoltaniAI/skill-translation-api.git
    cd skill-translation-api
    ```

2. Install the required packages:
    ```bash
    poetry install
    poetry shell
    ```

## Usage
    ```bash
    chmod +x run_app.sh && ./run_app.sh
    ```
Open your web browser and go to `http://localhost:8501`.
or you can run the backend and frontend with the follwoing commands
1. Start the FastAPI backend:
    ```bash
    uvicorn src.main:app
    ```

2. Run the Streamlit app:
    ```bash
    streamlit run src/app/app.py
    ```

3. Open your web browser and go to `http://localhost:8501`.

## Streamlit App

The Streamlit app provides an interactive interface for uploading the Excel file, selecting sheets and columns, and specifying target languages for translation.

### Key Features

- **File Upload**: Upload an Excel file containing skill descriptions.
- **Sheet and Column Selection**: Select the sheets and columns to translate.
- **Language Selection**: Choose target languages for translation.
- **Translation**: Send the selected data to the FastAPI backend for translation.
- **Download**: Download the translated Excel file.

## FastAPI Backend

The FastAPI backend handles the translation requests from the Streamlit app. It processes the uploaded file, performs translations using OpenAI's GPT models, and returns the translated file.

### Key Endpoints

- **POST /translate/**: Handles the translation of skill descriptions.
- **GET /download/{file_path}**: Serves the translated file for download.
