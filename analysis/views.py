from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import SetupForm
import os
import sys
from dotenv import load_dotenv
from src.api.grok_api import transcribe_setup
from src.checks.check_for_opponent import check_for_opponent
from src.database.setup_to_sql import process_game_setup

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))



def hello_world(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stratego Setup Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .nav { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #007bff; font-weight: bold; }
            .nav a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/add-setup/">Add Setup</a>
        </div>
        <h1>Welcome to Stratego Setup Analysis</h1>
        <p>This application helps you analyze and track your Stratego game setups.</p>
        <ul>
            <li><a href="/add-setup/">Add a new setup</a> - Upload an image and add game details</li>
        </ul>
    </body>
    </html>
    """
    return HttpResponse(html)

def add_setup(request):
    if request.method == 'POST':
        form = SetupForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get form data
                date_played = form.cleaned_data['date_played']
                opponent_name_input = form.cleaned_data['opponent_name']
                result = form.cleaned_data['result']
                moves = form.cleaned_data['moves']
                noob_killer = form.cleaned_data['noob_killer']
                setup_image = form.cleaned_data['setup_image']
                
                # Save the uploaded image temporarily
                file_name = default_storage.save(f'temp/{setup_image.name}', ContentFile(setup_image.read()))
                file_path = default_storage.path(file_name)
                
                # Process opponent details
                opponent_details = check_for_opponent(opponent_name_input)
                opponent_id = opponent_details[0]
                opponent_name = opponent_details[1]
                
                # Check if API key is loaded
                api_key = os.getenv("XAI_API_KEY")
                if not api_key:
                    raise ValueError("XAI_API_KEY not found in environment variables")
                
                # Transcribe the setup from the image
                transcribed_setup = transcribe_setup(file_path)
                
                # Create the user input dictionary (similar to original add_setup.py)
                user_input_dict = {
                    "date_played": date_played,
                    "opponent_id": opponent_id,
                    "opponent_name": opponent_name,
                    "result": result,
                    "moves": moves,
                    "noob_killer": noob_killer,
                    "setup": transcribed_setup
                }
                
                # Clean up temporary file
                default_storage.delete(file_name)
                
                # Process and save to database
                setup_id = process_game_setup(user_input_dict)
                
                # Add success message
                messages.success(request, f'Setup added successfully! Opponent: {opponent_name}, Result: {result}, Setup ID: {setup_id}')
                
                return redirect('add_setup')
                
            except Exception as e:
                error_msg = str(e)
                if "xAI API key is not set" in error_msg:
                    messages.error(request, 'xAI API key is not configured. Please set the XAI_API_KEY environment variable or add it to your .env file.')
                else:
                    messages.error(request, f'Error processing setup: {error_msg}')
                return render(request, 'analysis/add_setup.html', {'form': form})
    else:
        form = SetupForm()
    
    return render(request, 'analysis/add_setup.html', {'form': form})
