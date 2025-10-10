// Flask Backend Integration Service
const API_BASE_URL = 'http://localhost:8000'

export const identifyPlantWithCNN = async (imageFile) => {
  try {
    // Prepare image for Flask backend
    const formData = new FormData()
    formData.append('image', imageFile)
    
    // Connect to Flask backend endpoint
    const response = await fetch(`${API_BASE_URL}/api/plants/identify-and-care`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // Return the full plant data structure that PlantInfo expects
    if (result.success && result.care_data) {
      return {
        name: result.care_data.name,
        care: result.care_data.care || {},
        url: result.care_data.url,
        confidence: result.identification?.top_match?.confidence,
        predictions: result.identification?.predictions
      }
    }
    
    throw new Error('No plant data returned from backend')
    
  } catch (error) {
    console.error('Backend identification error:', error)
    
    // Fallback to mock identification while debugging
    return mockPlantIdentification(imageFile)
  }
}

// Mock function for development (remove when CNN model is ready)
const mockPlantIdentification = async (imageFile) => {
  // Import care data service for mock
  const { getPlantCareData } = await import('./plantDataService.js')
  
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  // Mock predictions based on your plant care data
  const availablePlants = [
    'Alocasia', 'Aloe', 'Anthurium', 'Begonia', 'Bird of Paradise',
    'Calathea', 'Chinese Evergreen', 'Ctenanthe', 'Dieffenbachia',
    'Dracaena', 'Ficus', 'Hypoestes', 'Ivy', 'Maranta', 'Money Tree',
    'Monstera', 'Peace Lily', 'Poinsettia', 'Pothos', 'Schefflera',
    'Snake Plant', 'Yucca', 'Zamioculcas Zamiifolia \'ZZ\''
  ]
  
  // Return random plant for demo (90% success rate)
  if (Math.random() < 0.9) {
    const selectedPlant = availablePlants[Math.floor(Math.random() * availablePlants.length)]
    const careData = await getPlantCareData(selectedPlant)
    
    if (careData) {
      return {
        name: careData.name,
        care: careData.care || {},
        url: careData.url,
        confidence: Math.random() * 0.3 + 0.7, // Mock confidence 70-100%
        predictions: [
          {
            name: selectedPlant,
            confidence: Math.random() * 0.3 + 0.7,
            mock: true
          }
        ]
      }
    } else {
      // If no care data found, return basic structure
      return {
        name: selectedPlant,
        care: {},
        url: null,
        confidence: Math.random() * 0.3 + 0.7,
        predictions: [
          {
            name: selectedPlant,
            confidence: Math.random() * 0.3 + 0.7,
            mock: true
          }
        ]
      }
    }
  } else {
    throw new Error('Model confidence too low')
  }
}

// Function to preprocess image for CNN (if needed)
export const preprocessImageForCNN = async (imageFile) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      // Resize to model input size (e.g., 224x224 for most CNN models)
      canvas.width = 224
      canvas.height = 224
      ctx.drawImage(img, 0, 0, 224, 224)
      
      canvas.toBlob(resolve, 'image/jpeg', 0.9)
    }
    
    img.src = URL.createObjectURL(imageFile)
  })
}