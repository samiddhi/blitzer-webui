#!/usr/bin/env python3
"""
Flask backend for Blitzer Web UI
Provides an API endpoint to interact with the blitzer CLI tool.
"""

import os
import subprocess
import sys
from flask import Flask, request, jsonify, render_template_string
from werkzeug.exceptions import BadRequest


def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Serve the main HTML page."""
        # Read and return the index.html file
        try:
            with open('index.html', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Frontend file not found. Please ensure index.html exists in the same directory as the server.", 404
    
    @app.route('/api/languages', methods=['GET'])
    def get_languages():
        """API endpoint that gets the available languages from blitzer."""
        try:
            # Execute the command to get available languages
            result = subprocess.run(
                ['blitzer', 'languages', 'list'],
                text=True,
                capture_output=True,
                check=False  # We'll check the result manually
            )
            
            # Check if the command executed successfully
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
                return jsonify({"error": f"Command failed: {error_msg}"}), 500
            
            # Parse the languages from the output - assuming one language code per line
            languages = [lang.strip() for lang in result.stdout.strip().split('\n') if lang.strip()]
            
            # Return the list of languages
            return jsonify({"languages": languages}), 200
            
        except FileNotFoundError:
            return jsonify({"error": "blitzer command not found. Make sure blitzer is installed and in your PATH"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/blitzer', methods=['POST'])
    def blitzer_api():
        """API endpoint that calls the blitzer CLI with the provided parameters."""
        try:
            data = request.get_json()
            
            # Validate required parameters
            if not data or 'text' not in data:
                return jsonify({"error": "Missing text in request"}), 400
            
            text = data['text']
            language = data.get('language', 'pli')
            lemmatize = data.get('lemmatize', False)  # New flag: -L / --lemmatize
            freq = data.get('freq', False)  # Flag: -f / --freq
            context = data.get('context', False)  # New flag: -c / --context  
            prompt = data.get('prompt', False)  # Flag: -p / --prompt
            src = data.get('src', False)  # Flag: -s / --src
            
            # Validate language by checking if it's in the list from blitzer
            result = subprocess.run(
                ['blitzer', 'languages', 'list'],
                text=True,
                capture_output=True,
                check=False
            )
            
            if result.returncode == 0:
                available_languages = [lang.strip() for lang in result.stdout.strip().split('\n') if lang.strip()]
                if language not in available_languages:
                    return jsonify({"error": f"Invalid language: {language}. Available options: {available_languages}"}), 400
            else:
                # If blitzer list fails, return an error
                return jsonify({"error": f"Could not fetch available languages: {result.stderr.strip() if result.stderr else 'Unknown error'}"}), 500
            
            # Build the command using new flag-based structure
            # For each boolean option, add the appropriate flag to ensure config doesn't override
            cmd = ['blitzer', 'blitz', '-l', language]
            
            # For each boolean option, add the appropriate flag
            # If the option is True, add the positive flag
            # If the option is False, add the negative flag to override config files
            cmd.append('-L' if lemmatize else '--no-lemmatize')
            cmd.append('-f' if freq else '--no-freq')
            cmd.append('-c' if context else '--no-context')
            cmd.append('-p' if prompt else '--no-prompt')
            cmd.append('-s' if src else '--no-src')
            
            # Execute the command with text input
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                check=False  # We'll check the result manually
            )
            
            # Check if the command executed successfully
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
                return jsonify({"error": f"Command failed: {error_msg}"}), 500
            
            return result.stdout, 200
            
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Command timed out"}), 500
        except FileNotFoundError:
            return jsonify({"error": "blitzer command not found. Make sure blitzer is installed and in your PATH"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
