# Google Drive Integration with Flask

This project is a Flask-based web application that integrates with Google Drive using OAuth 2.0 authentication. Users can authenticate with their Google account and perform actions like creating folders and uploading files to Google Drive.

## Features
- OAuth 2.0 authentication with Google
- Create folders in Google Drive
- Upload files to Google Drive
- Secure session handling

## Prerequisites
Before running the project, ensure you have the following installed:
- Python 3.x
- Flask
- `google-auth-oauthlib`
- `google-auth`
- `google-auth-httplib2`
- `google-api-python-client`

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/google-drive-flask.git
   cd google-drive-flask
   ```
2. Create a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up Google API credentials:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Drive API
   - Generate OAuth 2.0 client credentials and download `credentials.json`
   - Place `credentials.json` in the project root folder

## Running the Application
1. Set up the environment variable for local development:
   ```sh
   export OAUTHLIB_INSECURE_TRANSPORT=1  # On Windows, use `set OAUTHLIB_INSECURE_TRANSPORT=1`
   ```
2. Start the Flask application:
   ```sh
   python drive_integration.py
   ```
3. Open `http://localhost:5000/` in your browser to start using the app.

## Folder Structure
```
project-root/
│-- drive_integration.py  # Main application file
│-- templates/
│   └── drive_actions.html  # HTML template
│-- static/
│-- uploads/  # Temporary upload directory
│-- credentials.json  # Google API credentials
│-- requirements.txt  # Python dependencies
│-- README.md  # Project documentation
```

## Troubleshooting
- **Invalid session state:** Ensure session variables are set properly and try logging in again.
- **PermissionError on Windows:** If you get `[WinError 32]`, ensure the file is not in use before deleting it.
- **File Not Found Error:** Verify that the uploaded file exists before processing.

## License
This project is licensed under the MIT License.

