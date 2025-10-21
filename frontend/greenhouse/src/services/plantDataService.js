const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


export const getPlantImage = async (plantName) => {
  if (!plantName) return null
  
  try {
    const imageUrl = `${API_BASE_URL}/api/images/plant/${encodeURIComponent(plantName)}`
    return {
      url: imageUrl
    }
    
  } catch (error) {
    console.error('Error getting plant image URL:', error)
    return null
  }
}
