// Import your plant care data
import plantCareData from '../data/plant_care_data.json'

export const getPlantCareData = (plantName) => {
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
  
  // Handle common name variations from CNN model
  const nameMapping = {
    'zz plant': 'Zamioculcas Zamiifolia \'ZZ\'',
    'zz': 'Zamioculcas Zamiifolia \'ZZ\'',
    'zamioculcas': 'Zamioculcas Zamiifolia \'ZZ\'',
    'chinese evergreen': 'Chinese Evergreen',
    'aglaonema': 'Chinese Evergreen',
    'bird of paradise': 'Bird of Paradise',
    'strelitzia': 'Bird of Paradise',
    'prayer plant': 'Maranta',
    'polka dot plant': 'Hypoestes',
    'devil\'s ivy': 'Pothos',
    'golden pothos': 'Pothos',
    'sansevieria': 'Snake Plant',
    'mother in law tongue': 'Snake Plant'
  }
  
  if (!plant && nameMapping[normalizedName]) {
    plant = plantCareData.find(p => 
      p.name === nameMapping[normalizedName]
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