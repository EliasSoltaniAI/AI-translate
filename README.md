
# Skill Description Translator

This project is a Skill Description Translator that utilizes Streamlit for the frontend and FastAPI for the backend. It allows users to upload an Excel file, select sheets and columns to translate, and specify target languages for translation. The translations are performed using OpenAI's GPT models.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Streamlit App](#streamlit-app)
- [FastAPI Backend](#fastapi-backend)
- [Screenshots](#screenshots)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/skill-description-translator.git
    cd skill-description-translator
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the FastAPI backend:
    ```bash
    uvicorn app.main:app --reload
    ```

2. Run the Streamlit app:
    ```bash
    streamlit run app/frontend/app.py
    ```

3. Open your web browser and go to `http://localhost:8501`.

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   ├── utils.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   ├── app.py
├── data/
│   ├── translated_descriptions.xlsx
│   ├── back_translated_descriptions.xlsx
│   ├── sample_data.xlsx
├── params.yaml
├── llm_config.yaml
├── requirements.txt
```

## Streamlit App

The Streamlit app provides an interactive interface for uploading the Excel file, selecting sheets and columns, and specifying target languages for translation.

### Key Features

- **File Upload**: Upload an Excel file containing skill descriptions.
- **Sheet and Column Selection**: Select the sheets and columns to translate.
- **Language Selection**: Choose target languages for translation.
- **Translation**: Send the selected data to the FastAPI backend for translation.
- **Download**: Download the translated Excel file.

### Screenshots

![Streamlit App Screenshot](path_to_screenshot)

## FastAPI Backend

The FastAPI backend handles the translation requests from the Streamlit app. It processes the uploaded file, performs translations using OpenAI's GPT models, and returns the translated file.

### Key Endpoints

- **POST /translate/**: Handles the translation of skill descriptions.
- **GET /download/{file_path}**: Serves the translated file for download.

## Screenshots

### Streamlit App

![Streamlit App Upload](path_to_upload_screenshot)
![Streamlit App Selection](path_to_selection_screenshot)
![Streamlit App Translation](path_to_translation_screenshot)
![Streamlit App Download](path_to_download_screenshot)

### FastAPI

![FastAPI Endpoint](path_to_fastapi_screenshot)

## License

This project is proprietary and its source code is not publicly available. All rights reserved.
