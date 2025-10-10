// Import your plant care data - keeping as fallback
import plantCareData from '../data/plant_care_data.json'

const API_BASE_URL = 'http://localhost:8000'

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

export const getAllPlantNames = () => {
  return plantCareData.map(plant => plant.name)
}

export const getPlantCount = () => {
  return plantCareData.length
}

// For CNN model training - get all plant categories
export const getPlantCategories = () => {
  return plantCareData.map(plant => ({
    name: plant.name,
    hasFullCareData: Boolean(
      plant.care.light_requirements && 
      plant.care.watering_needs && 
      plant.care.soil_preferences
    )
  }))
}