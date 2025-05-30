# 🎨 Adaptive LUT - AI-Powered Color Grading

An AI-powered web application for video color grading. Upload video frames, describe your desired look in natural language, and receive generated LUT (.cube) files.

## Features

- 🤖 AI-powered color grading analysis
- ⚡ Instant LUT generation
- 📁 Industry-standard .cube file format
- 🎨 Beautiful, modern web interface
- 📱 Mobile-responsive design

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export SECRET_KEY="your-secret-key"
```

3. Run the app:
```bash
python3 app.py
```

Visit `http://localhost:5000`

## Deploy to Railway

1. Fork this repository on GitHub
2. Go to [Railway.app](https://railway.app)
3. Sign up with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select your forked repository
6. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Any random string for Flask sessions

Your app will be live in minutes!

## Deploy to Render

1. Fork this repository on GitHub
2. Go to [Render.com](https://render.com)
3. Sign up with GitHub
4. Click "New" → "Web Service"
5. Connect your GitHub repository
6. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 app.py`
7. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Any random string

## Project Structure

```
adaptive-lut-app/
├── app.py              # Main Flask application
├── lut_generator.py    # LUT generation logic
├── requirements.txt    # Python dependencies
├── static/
│   ├── index.html     # Frontend interface
│   ├── temp/          # Temporary uploads
│   └── luts/          # Generated LUT files
├── Procfile           # Deployment configuration
└── runtime.txt        # Python version specification
```

## API Endpoints

- `GET /` - Web interface
- `GET /api/health` - Health check
- `POST /api/process-lut` - Generate LUT from image and prompt
- `GET /static/<filename>` - Serve static files 