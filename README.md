# Blitzer Web UI

A clean, minimalist web interface for the Blitzer CLI tool. Provides a user-friendly interface for processing text with various language and mode options.

## Features

- Clean, minimalist design with digital minimalism principles
- Input and output text areas
- Language selection (Pali, Slovenian)
- Processing mode selection (word_list, lemma_list, word_list_context, lemma_list_context)
- Toggle switches for additional options (--freq, --prompt, --src)
- Clear and process buttons
- Responsive design for different screen sizes

## Requirements

- Python 3.7+
- Flask
- Blitzer CLI tool installed and in your PATH

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure the Blitzer CLI is installed:
   ```bash
   pip install -e /path/to/blitzer-cli
   ```

## Usage

1. Start the server:
   ```bash
   python server.py
   ```
   The server will start on port 8080 by default.

2. Open your browser and navigate to `http://localhost:8080`

3. Enter your text in the input area
4. Select language, mode and options
5. Click "Process Text" to see results in the output area

## API

The application exposes a single API endpoint:
- `POST /api/blitzer` - Process text with Blitzer CLI

Request body format:
```json
{
  "text": "Your input text here",
  "language": "pli",  // or "slv"
  "mode": "word_list",  // or "lemma_list", "word_list_context", "lemma_list_context"
  "freq": false,  // include frequency
  "prompt": false,  // include prompt
  "src": false  // include source text
}
```

## Configuration

The server can be configured using the PORT environment variable:
```bash
PORT=3000 python server.py
```