import { useState } from 'react'
import ImageUpload from './components/ImageUpload'
import PlantInfo from './components/PlantInfo'
import LoadingSpinner from './components/LoadingSpinner'
import './App.css'

function App() {
  const [plantData, setPlantData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePlantIdentified = (data) => {
    setPlantData(data)
    setError(null)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setPlantData(null)
  }

  const handleReset = () => {
    setPlantData(null)
    setError(null)
    setLoading(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌱 Plant Care Assistant</h1>
        <p>Upload a photo of your plant to get personalized care instructions</p>
      </header>

      <main className="app-main">
        {!plantData && !loading && (
          <ImageUpload 
            onPlantIdentified={handlePlantIdentified}
            onError={handleError}
            onLoadingChange={setLoading}
          />
        )}

        {loading && <LoadingSpinner />}

        {error && (
          <div className="error-container">
            <p className="error-message">❌ {error}</p>
            <button onClick={handleReset} className="retry-btn">
              Try Again
            </button>
          </div>
        )}

        {plantData && (
          <PlantInfo 
            plantData={plantData} 
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  )
}

export default App
