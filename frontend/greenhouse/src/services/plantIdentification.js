// CNN Model Integration Service
export const identifyPlantWithCNN = async (imageFile) => {
  try {
    // Prepare image for CNN model
    const formData = new FormData()
    formData.append('image', imageFile)
    
    // TODO: Replace with your actual CNN model endpoint when ready
    const response = await fetch('/api/identify-plant', {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    return result.plant_name || result.prediction || 'Unknown Plant'
    
  } catch (error) {
    console.error('CNN model error:', error)
    
    // Fallback to mock identification while CNN model is training
    return mockPlantIdentification(imageFile)
  }
}

// Mock function for development (remove when CNN model is ready)
const mockPlantIdentification = async (imageFile) => {
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 3000))
  
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
    return availablePlants[Math.floor(Math.random() * availablePlants.length)]
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