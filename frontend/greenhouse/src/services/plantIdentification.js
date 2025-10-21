const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const identifyPlantWithCNN = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)
    const response = await fetch(`${API_BASE_URL}/api/plants/identify`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success && result.plant) {
      const plantData = {
        name: result.plant.name,
        care: result.plant.care || {},
        url: result.plant.url,
        confidence: result.plant.confidence || null,
        predictions: result.all_predictions || [] 
      }
      return plantData
    }
    
    throw new Error('No plant data returned from backend')
    
  } catch (error) {
    console.error('Backend identification error:', error)
    return null
  }
}

