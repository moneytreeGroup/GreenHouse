// Test functions for Flask backend integration
const API_BASE_URL = 'http://localhost:8000'

// Test backend connection
export const testBackendConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`)
    const result = await response.json()
    console.log('Backend connection test:', result)
    return result
  } catch (error) {
    console.error('Backend connection failed:', error)
    return null
  }
}

// Test plant list endpoint
export const testPlantList = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/plants/list`)
    const result = await response.json()
    console.log('Plant list test:', result)
    return result
  } catch (error) {
    console.error('Plant list test failed:', error)
    return null
  }
}

// Test plant care endpoint
export const testPlantCare = async (plantName = 'monstera') => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/plants/care/${encodeURIComponent(plantName)}`)
    const result = await response.json()
    console.log(`Plant care test for ${plantName}:`, result)
    return result
  } catch (error) {
    console.error(`Plant care test for ${plantName} failed:`, error)
    return null
  }
}

// Test plant search endpoint
export const testPlantSearch = async (searchTerm = 'money') => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/plants/care/search?q=${encodeURIComponent(searchTerm)}`)
    const result = await response.json()
    console.log(`Plant search test for "${searchTerm}":`, result)
    return result
  } catch (error) {
    console.error(`Plant search test for "${searchTerm}" failed:`, error)
    return null
  }
}

// Test image upload (requires a file input)
export const testImageUpload = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)
    
    const response = await fetch(`${API_BASE_URL}/api/plants/identify-and-care`, {
      method: 'POST',
      body: formData,
    })
    
    const result = await response.json()
    console.log('Image upload test:', result)
    return result
  } catch (error) {
    console.error('Image upload test failed:', error)
    return null
  }
}

// Run all tests
export const runAllTests = async () => {
  console.log('🧪 Running Flask Backend Tests...')
  
  await testBackendConnection()
  await testPlantList()
  await testPlantCare('monstera')
  await testPlantCare('snake plant')
  await testPlantSearch('money')
  await testPlantSearch('light')
  
  console.log('✅ Backend tests completed!')
}
