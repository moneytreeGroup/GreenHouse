// Import your plant care data - keeping as fallback
import plantCareData from '../data/plant_care_data.json'

const API_BASE_URL = 'http://localhost:5000'

export const getPlantCareData = async (plantName) => {
  if (!plantName) return null
  
  try {
    // Try to get data from Flask backend first
    const response = await fetch(`${API_BASE_URL}/api/plants/care/${encodeURIComponent(plantName)}`)
    
    if (response.ok) {
      const result = await response.json()
      if (result.success && result.plant) {
        return result.plant
      }
    }
    
    // Fallback to local data if backend fails
    return getLocalPlantCareData(plantName)
    
  } catch (error) {
    console.error('Error fetching from backend, using local data:', error)
    return getLocalPlantCareData(plantName)
  }
}

// Simple function to get plant image from backend
export const getPlantImage = async (plantName) => {
  if (!plantName) return null
  
  try {
    // Simple path: just return the image URL directly
    const imageUrl = `${API_BASE_URL}/api/images/plant/${encodeURIComponent(plantName)}`
    return {
      url: imageUrl
    }
    
  } catch (error) {
    console.error('Error getting plant image URL:', error)
    return null
  }
}

// Fallback function using local data
const getLocalPlantCareData = (plantName) => {
  if (!plantName) return null
  
  // Normalize plant name for matching
  const normalizedName = plantName.toLowerCase().trim()
  
  // Direct match
  let plant = plantCareData.find(p => 
    p.name.toLowerCase() === normalizedName
  )
  
  // Partial match if direct match fails
  if (!plant) {
    plant = plantCareData.find(p => 
      p.name.toLowerCase().includes(normalizedName) ||
      normalizedName.includes(p.name.toLowerCase())
    )
  }

  return plant
}