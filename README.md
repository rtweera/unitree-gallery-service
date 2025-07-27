# Unitree Gallery Service

A FastAPI-based image gallery service that allows users to upload, view, and download images with QR code generation for easy sharing.

## 🚀 Features

- **Image Upload**: Upload images via API endpoint
- **Gallery View**: Browse images in an elegant web interface
- **Latest Image View**: Display the most recently uploaded image
- **QR Code Generation**: Automatic QR code creation for easy image sharing
- **Download Support**: Direct image download functionality
- **Image Management**: Delete individual images or all images
- **Responsive Design**: Modern, mobile-friendly interface
- **Health Check**: Service status monitoring

## 📋 Project Structure

```
unitree-gallery-service/
├── main.py                 # FastAPI application entry point
├── pyproject.toml          # Project configuration and dependencies
├── requirements.txt        # Auto-generated dependencies
├── uv.lock                 # Dependency lock file
├── .env.example            # Environment variables template
├── api/
│   ├── endpoints.py        # API route handlers
│   └── services.py         # Business logic and utilities
└── templates/
    ├── gallery.html        # Main gallery interface
    ├── latest_image.html   # Latest image display
    └── old_gallery.html    # Alternative gallery view
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Web Server**: Uvicorn
- **Templating**: Jinja2
- **QR Code**: qrcode library
- **Environment**: python-dotenv
- **File Handling**: python-multipart

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd unitree-gallery-service
   ```

2. **Install dependencies**
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Using uv (recommended):
   ```bash
   uv pip sync requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your deployment URL:
   ```
   DEPLOYED_URL=http://localhost:8000
   ```

4. **Create required directories**
   The application will automatically create these directories:
   - `images/` - For storing uploaded images
   - `qr/` - For storing generated QR codes

## 🚀 Running the Application

### Development Mode

```bash
python main.py
```

The application will start on `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📖 API Documentation

Once the application is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative API Docs**: `http://localhost:8000/redoc`

### Key Endpoints

#### Health & Stats
- `GET /health` - Health check
- `GET /stats` - Gallery statistics

#### Image Management
- `POST /upload` - Upload an image
- `GET /images/{image_id}` - Serve specific image
- `GET /download/{image_id}` - Download image
- `DELETE /delete/{image_id}` - Delete specific image
- `DELETE /delete` - Delete all images

#### QR Codes
- `GET /qr/{image_id}` - Get QR code for image

#### Web Interface
- `GET /` - Redirects to latest image
- `GET /latest` - Latest image view
- `GET /gallery` - Main gallery interface
- `GET /old-gallery` - Alternative gallery view

## 🖼️ Web Interface

### Gallery View (`/gallery`)
- **Thumbnail sidebar**: Browse all uploaded images
- **Main display**: View selected image in full size
- **QR code panel**: Scan to download current image
- **Refresh button**: Reload the gallery

### Latest Image View (`/latest`)
- Displays the most recently uploaded image
- Includes QR code for easy sharing
- Simple, focused interface

## 📱 Usage Examples

### Upload an Image
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@image.jpg"
```

### Get Gallery Stats
```bash
curl -X GET "http://localhost:8000/stats"
```

### Download an Image
```bash
curl -X GET "http://localhost:8000/download/img_123.jpg" \
     --output downloaded_image.jpg
```

## 🔧 Configuration

### Environment Variables

- `DEPLOYED_URL`: Base URL for the deployed service (used in QR codes)
  - Default: `http://localhost:5000`
  - Example: `https://your-domain.com`

### Directory Structure

The application automatically creates and manages:
- `images/` - Stores uploaded images (JPG format)
- `qr/` - Stores generated QR code images (PNG format)

## 🎨 Frontend Features

### Gallery Interface
- **Responsive design** with mobile-friendly layout
- **Thumbnail navigation** with hover effects
- **Click-to-select** image functionality
- **Automatic QR code generation** for each image
- **Modern styling** with gradient backgrounds and shadows

### Styling
- CSS Grid and Flexbox layouts
- Smooth transitions and hover effects
- Professional color scheme
- Responsive breakpoints

## 🐛 Troubleshooting

### Common Issues

1. **"DEPLOYED_URL environment variable is not set"**
   - Ensure your `.env` file exists and contains `DEPLOYED_URL`

2. **Images not displaying**
   - Check that the `images/` directory exists and is writable
   - Verify file permissions

3. **QR codes not generating**
   - Ensure the `qr/` directory exists and is writable
   - Check the `DEPLOYED_URL` configuration

### Logs

The application provides console logging for debugging:
- Image upload status
- File operations
- Error messages

## 📄 License

This project is part of the WSO2Con Gallery Service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions, please check the API documentation at `/docs` when the service is running.
