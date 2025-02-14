from flask import Flask, redirect, url_for, session, request, render_template, flash
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP (for local development)

# Path to the credentials file
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

@app.route('/')
def index():
    """ Check if the user is authenticated; if not, redirect to authorization """
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    return redirect(url_for('drive_actions'))  # Redirect to drive actions after login

@app.route('/authorize')
def authorize():
    """ Redirect the user to Google's OAuth 2.0 authorization page """
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state  # ✅ Store state in session
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """ Handle OAuth callback from Google """
    
    # ✅ Check if 'state' exists in session
    if 'state' not in session:
        flash("Session expired. Please try logging in again.", "error")
        return redirect(url_for('index'))

    # ✅ Validate the received state
    if session['state'] != request.args.get('state'):
        flash("Invalid session state. Please try again.", "error")
        return redirect(url_for('index'))

    # ✅ Recreate Flow object before fetching the token
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session['state'],
        redirect_uri='http://localhost:5000/callback'
    )

    # ✅ Fetch OAuth token
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('drive_actions'))

@app.route('/drive_actions', methods=['GET', 'POST'])
def drive_actions():
    """ Display Drive actions only if the user is authenticated """
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    try:
        credentials = Credentials(**session['credentials'])
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        flash(f"Authentication error: {str(e)}. Please reauthorize.", "error")
        session.pop('credentials', None)
        return redirect(url_for('authorize'))

    if request.method == 'POST':
        action = request.form.get('action')
        folder_id = request.form.get('folder_id')

        if action == 'create_folder':
            folder_name = request.form.get('folder_name')
            if folder_name:
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = drive_service.files().create(body=file_metadata, fields='id').execute()
                flash(f'Folder "{folder_name}" created successfully.')
                folder_id = folder.get('id')

        if action == 'upload_file':
            file = request.files.get('file')  # ✅ Get file safely
            
            if file:
                file_path = os.path.join("uploads", file.filename)  # ✅ Save locally first
                file.save(file_path)

                # ✅ Use `with open(...)` to ensure file is closed before uploading
                with open(file_path, "rb") as f:
                    media = MediaFileUpload(file_path, mimetype=file.content_type)
                    file_metadata = {'name': file.filename}
                    if folder_id:
                        file_metadata['parents'] = [folder_id]

                    drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                flash(f'File "{file.filename}" uploaded successfully.')

                # ✅ Ensure file is closed before deleting
                try:
                    os.remove(file_path)  # Delete the local file
                except PermissionError:
                    flash(f'Could not delete temporary file: {file.filename}. It may be in use.', 'error')
            else:
                flash("No file was uploaded. Please select a file first.")

    session['credentials'] = credentials_to_dict(credentials)
    return render_template('drive_actions.html')

def credentials_to_dict(credentials):
    """ Convert OAuth credentials to dictionary for session storage """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")  # Create uploads directory if not exists
    app.run(debug=True)
