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
            mode = data.get('mode', 'word_list')
            freq = data.get('freq', False)
            prompt = data.get('prompt', False)
            src = data.get('src', False)
            
            # Validate language and mode
            valid_languages = ['pli', 'slv']
            valid_modes = ['word_list', 'lemma_list', 'word_list_context', 'lemma_list_context']
            
            if language not in valid_languages:
                return jsonify({"error": f"Invalid language: {language}. Valid options: {valid_languages}"}), 400
            
            if mode not in valid_modes:
                return jsonify({"error": f"Invalid mode: {mode}. Valid options: {valid_modes}"}), 400
            
            # Build the command
            cmd = ['blitzer', language, mode]
            
            if freq:
                cmd.append('--freq')
            if prompt:
                cmd.append('--prompt')
            if src:
                cmd.append('--src')
            
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