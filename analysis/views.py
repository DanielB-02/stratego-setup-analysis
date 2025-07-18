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
from PIL import Image, ImageEnhance

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def enhance_image_contrast(image_path, brightness_factor=1.2, contrast_factor=1.3):
    """
    Enhance the brightness and contrast of an image for better OCR results.
    
    Args:
        image_path: Path to the input image
        brightness_factor: Factor to increase brightness (1.0 = no change, >1.0 = brighter)
        contrast_factor: Factor to increase contrast (1.0 = no change, >1.0 = higher contrast)
    
    Returns:
        Tuple of (enhanced_path, enhanced_base64_data_url)
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Enhance brightness
            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(brightness_factor)
            
            # Enhance contrast
            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(contrast_factor)
            
            # Save the enhanced image
            enhanced_path = image_path.replace('.', '_enhanced.')
            img.save(enhanced_path, 'JPEG', quality=95)
            
            # Create base64 data URL for browser display
            import base64
            import io
            
            # Convert enhanced image to base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            enhanced_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            enhanced_data_url = f"data:image/jpeg;base64,{enhanced_base64}"
            
            return enhanced_path, enhanced_data_url
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return image_path, None  # Return original path if enhancement fails


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
        # Check if this is a JSON edit resubmission
        if 'edited_json' in request.POST:
            return handle_json_edit(request)
        
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
                
                # Enhance image contrast and brightness for better OCR
                enhanced_file_path, enhanced_data_url = enhance_image_contrast(file_path)
                
                # Convert image to base64 for error display
                import base64
                setup_image.seek(0)
                image_data = setup_image.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                image_mimetype = setup_image.content_type or 'image/jpeg'
                error_image_url = f"data:{image_mimetype};base64,{image_base64}"
                
                # Process opponent details
                opponent_details = check_for_opponent(opponent_name_input)
                opponent_id = opponent_details[0]
                opponent_name = opponent_details[1]
                
                # Check if API key is loaded
                api_key = os.getenv("XAI_API_KEY")
                if not api_key:
                    raise ValueError("XAI_API_KEY not found in environment variables")
                
                # Transcribe the setup from the enhanced image
                transcribed_setup = transcribe_setup(enhanced_file_path)
                
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
                
                # Clean up temporary files (keep error file for potential display)
                default_storage.delete(file_name)
                # Also clean up the enhanced image file
                try:
                    if enhanced_file_path != file_path and os.path.exists(enhanced_file_path):
                        os.remove(enhanced_file_path)
                except:
                    pass
                
                # Process and save to database
                setup_id = process_game_setup(user_input_dict)
                
                # No need to clean up error file since we're using base64
                
                # Add success message
                messages.success(request, f'Setup added successfully! Opponent: {opponent_name}, Result: {result}, Setup ID: {setup_id}')
                
                return redirect('add_setup')
                
            except Exception as e:
                error_msg = str(e)
                if "xAI API key is not set" in error_msg:
                    messages.error(request, 'xAI API key is not configured. Please set the XAI_API_KEY environment variable or add it to your .env file.')
                    return render(request, 'analysis/add_setup.html', {'form': form})
                elif any(keyword in error_msg for keyword in ['piece', 'count', 'Incorrect count', 'Invalid piece type', 'Amount of pieces']):
                    # This is a piece configuration error - allow JSON editing
                    import json
                    transcribed_setup = locals().get('transcribed_setup', {})
                    transcribed_setup_json = format_setup_json(transcribed_setup)
                    
                    # Clean up main temp file and enhanced image
                    try:
                        default_storage.delete(file_name)
                        if enhanced_file_path != file_path and os.path.exists(enhanced_file_path):
                            os.remove(enhanced_file_path)
                    except:
                        pass
                    
                    # Use the pre-saved error image URL or enhanced image URL
                    setup_image_url = locals().get('error_image_url', None)
                    enhanced_image_url = locals().get('enhanced_data_url', None)
                    
                    context = {
                        'form': form,
                        'json_error': True,
                        'error_message': error_msg,
                        'transcribed_setup': transcribed_setup,
                        'transcribed_setup_json': transcribed_setup_json,
                        'form_data': {
                            'date_played': date_played,
                            'opponent_name_input': opponent_name_input,
                            'result': result,
                            'moves': moves,
                            'noob_killer': noob_killer,
                            'opponent_id': opponent_id,
                            'opponent_name': opponent_name,
                            'setup_image_url': setup_image_url,
                            'enhanced_image_url': enhanced_image_url,
                        }
                    }
                    return render(request, 'analysis/add_setup.html', context)
                else:
                    messages.error(request, f'Error processing setup: {error_msg}')
                    return render(request, 'analysis/add_setup.html', {'form': form})
    else:
        form = SetupForm()
    
    return render(request, 'analysis/add_setup.html', {'form': form})


def handle_json_edit(request):
    """Handle the JSON edit resubmission"""
    import json
    
    try:
        # Get the edited JSON and form data
        edited_json_str = request.POST.get('edited_json', '')
        edited_setup = json.loads(edited_json_str)
        
        # Reconstruct form data
        form_data = {
            'date_played': request.POST.get('date_played'),
            'opponent_name_input': request.POST.get('opponent_name_input'),
            'result': request.POST.get('result'),
            'moves': int(request.POST.get('moves')),
            'noob_killer': int(request.POST.get('noob_killer')),
            'opponent_id': int(request.POST.get('opponent_id')) if request.POST.get('opponent_id') else None,
            'opponent_name': request.POST.get('opponent_name'),
        }
        
        # Create user input dictionary with edited setup
        user_input_dict = {
            "date_played": form_data['date_played'],
            "opponent_id": form_data['opponent_id'],
            "opponent_name": form_data['opponent_name'],
            "result": form_data['result'],
            "moves": form_data['moves'],
            "noob_killer": form_data['noob_killer'],
            "setup": edited_setup
        }
        
        # Process and save to database
        setup_id = process_game_setup(user_input_dict)
        
        # Add success message
        messages.success(request, f'Setup added successfully with edited JSON! Opponent: {form_data["opponent_name"]}, Result: {form_data["result"]}, Setup ID: {setup_id}')
        
        return redirect('add_setup')
        
    except json.JSONDecodeError:
        # JSON syntax error - show the JSON editor again with the invalid JSON
        error_message = 'Invalid JSON format. Please check your JSON syntax and try again.'
        context = create_json_error_context(request, error_message, edited_json_str)
        return render(request, 'analysis/add_setup.html', context)
        
    except Exception as e:
        error_msg = str(e)
        # Check if it's a piece configuration error
        if any(keyword in error_msg for keyword in ['piece', 'count', 'Incorrect count', 'Invalid piece type', 'Amount of pieces']):
            # Show the JSON editor again with the current JSON and new error message
            context = create_json_error_context(request, error_msg, edited_json_str)
            return render(request, 'analysis/add_setup.html', context)
        else:
            # Other errors - show generic error and redirect
            messages.error(request, f'Error processing edited setup: {error_msg}')
            return redirect('add_setup')


def create_json_error_context(request, error_message, json_str):
    """Create context for JSON error display"""
    import json
    
    # Try to parse JSON for custom formatting, fallback to raw string if invalid
    try:
        parsed_json = json.loads(json_str)
        formatted_json = format_setup_json(parsed_json)
    except:
        formatted_json = json_str
    
    # Get image URLs from hidden fields if available
    setup_image_url = request.POST.get('setup_image_url', None)
    enhanced_image_url = request.POST.get('enhanced_image_url', None)
    
    return {
        'form': SetupForm(),  # Empty form since we're in error state
        'json_error': True,
        'error_message': error_message,
        'transcribed_setup_json': formatted_json,
        'form_data': {
            'date_played': request.POST.get('date_played', ''),
            'opponent_name_input': request.POST.get('opponent_name_input', ''),
            'result': request.POST.get('result', ''),
            'moves': request.POST.get('moves', ''),
            'noob_killer': request.POST.get('noob_killer', ''),
            'opponent_id': request.POST.get('opponent_id', ''),
            'opponent_name': request.POST.get('opponent_name', ''),
            'setup_image_url': setup_image_url,
            'enhanced_image_url': enhanced_image_url,
        }
    }


def format_setup_json(setup_dict):
    """Format setup JSON in the compact single-line array format"""
    import json
    if not setup_dict:
        return "{}"
    
    lines = ["{"]
    for i, (key, value) in enumerate(setup_dict.items()):
        # Format each row as a single line with proper JSON formatting
        comma = "," if i < len(setup_dict) - 1 else ""
        # Use json.dumps to properly format the value with double quotes
        formatted_value = json.dumps(value)
        line = f'    "{key}": {formatted_value}{comma}'
        lines.append(line)
    lines.append("}")
    
    return "\n".join(lines)
