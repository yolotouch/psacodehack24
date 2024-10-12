import openai
from django.http import JsonResponse
from django.conf import settings
import json
from django.shortcuts import render

def language_detection_page(request):
    return render(request, 'detect_language.html')


# Function to detect language using OpenAI API
def detect_language(message):
    """
    Detects the language of a given message using the OpenAI API.
    """
    # Set the OpenAI API key
    openai.api_key = settings.OPENAI_API_KEY

    # Prepare the messages for the chat model
    messages = [
        {"role": "user", "content": f"What language is this text? '{message}'. Please respond with just the language name."}
    ]

    try:
        # Call OpenAI's chat model to identify the language
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or gpt-3.5-turbo
            messages=messages,
            max_tokens=10  # Keep the response short since we only need the language name
        )
        # Extract the detected language
        detected_language = response['choices'][0]['message']['content'].strip()
    
        if not detected_language:
            return "Could not determine the language."
        
        return detected_language

    except Exception as e:
        return f"Error: {str(e)}"

def translate_to_english(message):
    """
    Translates the given message to English using the OpenAI API,
    specifying the original language.
    """
    openai.api_key = settings.OPENAI_API_KEY

    original_language = detect_language(message)
    # Prepare the prompt for translation, including the original language
    prompt = f"Translate the following text from {original_language} to English: '{message}'. Provide only the translated text without any additional explanation. This is used in a professional work setting, please ensure proper punctuation and grammar."

    try:
        # Call OpenAI's chat model to translate the text
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60  # Adjust as needed to ensure full translation
        )
        # Extract the translated text
        translated_text = response['choices'][0]['message']['content'].strip()
        return translated_text

    except Exception as e:
        return f"Error: {str(e)}"
    
def translate_to_language(message, target_language):
    """
    Translates the given message to the specified target language using the OpenAI API,
    specifying the original language.
    """
    openai.api_key = settings.OPENAI_API_KEY

    original_language = detect_language(message)
    new_message = translate_to_english(message)
    
    # Ensure the original language is valid before proceeding
    if "Error:" in original_language:
        return f"Error detecting language: {original_language}"

    # Prepare the prompt for translation, including the original language
    prompt = f"Translate the following text from English to {target_language}: '{new_message}'. Provide only the translated text without any additional explanation. This is used in a professional work setting, please ensure proper punctuation and grammar."

    try:
        # Call OpenAI's chat model to translate the text
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60  # Adjust as needed to ensure full translation
        )
        # Extract the translated text
        translated_text = response['choices'][0]['message']['content'].strip()
        
        if not translated_text:
            return "Translation returned empty. Please try again."
        
        return translated_text

    except Exception as e:
        return f"Error during translation: {str(e)}"

def detect_language_view(request):
    if request.method == 'POST':
        # Parse the incoming request
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        target_language = data.get('target_language', 'English')  # Default to English if not specified

        if not message:
            return JsonResponse({"error": "No message provided"}, status=400)

        # Detect the language of the provided message
        detected_language = detect_language(message)

        # Check if the detected language is not the target language
        if detected_language.lower() != target_language.lower():
            # Translate the message to the target language, specifying the original language
            translated_message = translate_to_language(message, target_language)
            return JsonResponse({
                "detected_language": detected_language,
                "translated_message": translated_message
            }, status=200)

        return JsonResponse({
            "detected_language": detected_language,
            "translated_message": message
        }, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


