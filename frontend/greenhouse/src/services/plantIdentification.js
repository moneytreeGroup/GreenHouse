// Flask Backend Integration Service
const API_BASE_URL = 'http://localhost:5000'

export const identifyPlantWithCNN = async (imageFile) => {
  try {
    // Prepare image for Flask backend
    const formData = new FormData()
    formData.append('image', imageFile)
    // Connect to Flask backend endpoint
    const response = await fetch(`${API_BASE_URL}/api/plants/identify`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // Return the full plant data structure that PlantInfo expects
    if (result.success && result.plant) {
      const plantData = {
        name: result.plant.name,
        care: result.plant.care || {},
        url: result.plant.url,
        confidence: result.plant.confidence || null,
        predictions: result.all_predictions || [] // Now available in the same response!
      }
      return plantData
    }
    
    throw new Error('No plant data returned from backend')
    
  } catch (error) {
    console.error('Backend identification error:', error)
    return null
  }
}

