# Flask Backend for Plant Recognition App

This is the backend API for the Plant Recognition application built with Flask.

## Features

- **Plant Identification**: Upload images and get plant species predictions
- **Plant Care Data**: Retrieve detailed care instructions for identified plants
- **Image Processing**: Automatic image preprocessing and validation
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Configured for React frontend

## API Endpoints

### Plant Identification
- `POST /api/plants/identify` - Identify plant from uploaded image
- `POST /api/plants/identify-and-care` - Identify plant and get care instructions

### Plant Care Information
- `GET /api/plants/care/<plant_name>` - Get care data for specific plant
- `GET /api/plants/care/search?q=<search_term>` - Search plants by name/care keywords
- `GET /api/plants/list` - Get list of all available plants

### File Upload
- `POST /api/upload/image` - Upload and validate image file
- `POST /api/upload/validate` - Validate image without saving
- `POST /api/upload/cleanup` - Clean up temporary files

## Setup and Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up plant care data**:
   - Make sure `plant_care_data.json` exists in the project root
   - This file is created by running the web scraper

4. **Run the application**:
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## Model Integration

The backend is ready for PyTorch model integration:

1. **Train your model** and save it as a `.pth` file
2. **Update the model class** in `models/plant_model.py`:
   - Set the correct number of classes
   - Update the class names list
   - Modify architecture if needed
3. **Load your model** by providing the path to `PlantModel(model_path="path/to/model.pth")`

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── routes/
│   ├── plant_routes.py    # Plant identification & care endpoints
│   └── upload_routes.py   # File upload endpoints
├── services/
│   ├── plant_care_service.py  # Plant care data management
│   └── image_processor.py     # Image preprocessing
├── models/
│   └── plant_model.py     # PyTorch model wrapper
└── uploads/               # Temporary file storage
```

## Development

For development, the app runs with mock predictions until you provide a trained model. The mock predictions simulate realistic confidence scores for testing.

## Environment Variables

- `SECRET_KEY`: Flask secret key (defaults to 'dev-secret-key')
- `MAX_CONTENT_LENGTH`: Maximum file upload size (defaults to 16MB)

## Error Handling

The API includes comprehensive error handling:
- File validation errors
- Image processing errors
- Model prediction errors
- Database lookup errors

All errors return appropriate HTTP status codes and descriptive messages.
