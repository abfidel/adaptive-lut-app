# 🎨 Adaptive LUT - AI-Powered Color Grading

Transform your videos with intelligent color grading! Upload a frame, describe your vision, and get professional **downloadable .cube LUT files** instantly.

## ✨ Features

- 🤖 **AI-Powered Analysis** - GPT-4o Vision analyzes your images and creative vision
- 📁 **Downloadable .cube Files** - Professional LUT files compatible with all major editing software
- 🖼️ **Live Preview** - See your LUT applied to test images instantly
- 🎯 **Smart Style Recognition** - Recognizes cinematic, vintage, warm, cool, and blockbuster styles
- ⚡ **Instant Results** - Generate professional-grade LUTs in seconds
- 🎬 **Industry Standard** - Compatible with DaVinci Resolve, Premiere Pro, Final Cut Pro, and more

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/abfidel/adaptive-lut-app.git
cd adaptive-lut-app
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get yours at: https://platform.openai.com/api-keys
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
SECRET_KEY=your-secret-key-here
PORT=5001
```

### 4. Run the Application
```bash
python3 app.py
```

Visit **http://127.0.0.1:5001** in your browser! 🎉

## 🎯 How to Use

1. **Upload an Image** - Drag & drop or click to upload (JPEG/PNG, max 10MB)
2. **Describe Your Vision** - Tell the AI what look you want:
   - *"warm cinematic sunset with golden hour lighting"*
   - *"cool modern teal and orange blockbuster style"*
   - *"vintage film look with enhanced contrast"*
   - *"moody dramatic style with deep shadows"*
3. **Generate LUT** - AI analyzes your image and creates professional adjustments
4. **Download & Preview** - Get your .cube file and see a live preview!

## 🎨 Supported Styles

- **Warm Cinematic** - Golden hour, sunset, amber tones
- **Cool Modern** - Teal, blue, winter, cyan aesthetics  
- **Vintage Film** - Kodak, Fuji, analog, retro characteristics
- **Moody Dramatic** - High contrast, deep shadows, bold look
- **Bright & Airy** - Light, clean, lifted shadows
- **Teal & Orange** - Hollywood blockbuster style

## 🛠️ Technical Details

### LUT Generation
- **32³ cube resolution** (industry standard)
- **Real color transformations**:
  - Temperature adjustments (-100 to +100)
  - Contrast and exposure controls
  - Saturation and vibrance
  - Color wheel adjustments (shadows/midtones/highlights)
- **Professional .cube format** compatible with all major software

### AI Integration
- **GPT-4o Vision API** for intelligent image analysis
- **Fallback simulation** when OpenAI is unavailable
- **Smart prompt parsing** for style recognition

## 📁 Project Structure
```
adaptive-lut-app/
├── app.py              # Main Flask application
├── lut_generator.py    # LUT creation engine
├── static/
│   ├── index.html      # Frontend interface
│   ├── temp/          # Uploaded images & previews
│   └── luts/          # Generated .cube files
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── README.md          # This file
```

## 🚀 Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
3. Deploy automatically!

### Manual Deployment
```bash
# Set environment variables
export OPENAI_API_KEY="your-api-key"
export PORT=8080

# Run production server
python3 app.py
```

## 🔧 API Endpoints

- `GET /` - Main application interface
- `GET /api/health` - Health check & OpenAI status
- `POST /api/process-lut` - Generate LUT from image + prompt
- `GET /download/lut/<filename>` - Download .cube file
- `GET /static/<path>` - Serve static files

## 🎬 Editing Software Compatibility

Your generated .cube files work with:
- **DaVinci Resolve** - Import in Color page → LUTs
- **Adobe Premiere Pro** - Effects → Color Correction → Apply LUT
- **Final Cut Pro** - Effects → Color → Custom LUT
- **Adobe After Effects** - Effects → Color Correction → Apply Color LUT
- **Avid Media Composer** - Color Correction → LUT

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o Vision API
- Flask community for the excellent web framework
- Color science community for LUT standards

---

**Made with ❤️ for filmmakers and content creators**

*Transform your footage with AI-powered precision* 