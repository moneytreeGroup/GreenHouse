# 🌿 GreenHouse

Mini-project for the University of Helsinki course Introduction to Data Science 2025.
It is a full-stack web application that uses machine learning to identify plant species from images and provides detailed care instructions to help you keep your plants healthy and thriving.
Backend: https://greenhouse-backend-ju79.onrender.com
Frontend: https://greenhouse-frontend.onrender.com
CNN Model: https://lauras1-plant-classifier.hf.space/
Manual: Go to https://greenhouse-backend-ju79.onrender.com/api/plants/model/info to view model information. If the model is not connected, go to the CNN model page and start the model.

## 📋 Overview

GreenHouse combines computer vision and plant care knowledge to make plant identification and care simple. Upload a photo of your plant, and the app will:
- Identify the plant species using a trained deep learning model
- Provide comprehensive care instructions including watering, light, humidity, and temperature requirements
- Offer tips for common problems and plant maintenance

## 🌟 Features

- **Image-Based Plant Recognition**: Upload images to identify plant species from 19+ different houseplants
- **AI-Powered Classification**: Uses PyTorch-based deep learning model for accurate species identification
- **Detailed Care Instructions**: Get personalized care guides for each identified plant
- **Modern UI**: Clean, responsive React interface built with Vite
- **REST API**: Flask backend with organized routes and services

## 🏗️ Project Structure

```
greenhouse_project/
├── backend/                 # Flask API server
│   ├── app.py              # Main application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # ML model definitions
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic and services
│   ├── plant_images/       # Training data (19 plant species)
│   └── plant_care_data.json # Plant care information database
| 
└── frontend/
    └── greenhouse/         # React application
        ├── src/
        │   ├── components/ # React components
        │   └── services/   # API client services
        └── package.json
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **PyTorch** - Deep learning framework
- **Torchvision** - Computer vision models
- **Pillow** - Image processing
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React** - UI framework
- **Vite** - Build tool and dev server
- **Recharts** - Data visualization
- **Modern JavaScript (ES6+)**

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend/greenhouse
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🌱 Supported Plant Species

The app can currently identify 19 different plant species:
- Aloe
- Anthurium
- Bird of Paradise
- Chinese Evergreen
- Ctenanthe
- Dieffenbachia
- Dracaena
- Ficus
- Hypoestes
- Ivy
- Maranta
- Money Tree
- Monstera
- Peace Lily
- Poinsettia
- Pothos
- Schefflera
- Snake Plant
- ZZ Plant (Zamioculcas zamiifolia)

## 📡 API Endpoints

- `GET /` - Health check
- `POST /api/upload` - Upload plant image for identification
- `GET /api/plants` - Get all plant information
- `GET /api/plants/{name}` - Get specific plant care details
- `GET /api/images/{filename}` - Retrieve plant images

## 🙏 Acknowledgments

This project uses the [House Plant Species dataset](https://www.kaggle.com/datasets/kacpergregorowicz/house-plant-species) by Kacper Gregorowicz (KAKA) from Kaggle for training the plant classification model. We are grateful for this valuable resource that made our plant recognition feature possible.

Plant care instructions and information were gathered from [House Plant Resource](https://www.houseplantresource.com/), an excellent resource for comprehensive plant care guides. We appreciate their detailed and accessible plant care information.

## 📝 License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

This means you are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- **NonCommercial** — You may not use the material for commercial purposes
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license

The training data used in this project is subject to CC BY-NC-SA 4.0, and therefore this license applies to the entire project.

## 👥 Authors

Created by the MoneyTree Group: Niko, Laura and Elina.

---

Made with 💚 for plant lovers everywhere
