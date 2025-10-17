import { useState } from 'react'
import ImageUpload from './components/ImageUpload'
import PlantInfo from './components/PlantInfo'
import LoadingSpinner from './components/LoadingSpinner'
import PredictionSelector from './components/PredictionSelector'
import './App.css'

function App() {
  const [plantData, setPlantData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showPredictions, setShowPredictions] = useState(false)
  const [predictions, setPredictions] = useState([])
  const [selectedFromPredictions, setSelectedFromPredictions] = useState(false)


  const handlePlantIdentified = (data) => {
    setPlantData(data)
    setError(null)
    setShowPredictions(false)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setPlantData(null)
    setShowPredictions(false)
  }

  const handleReset = () => {
    setPlantData(null)
    setError(null)
    setLoading(false)
    setShowPredictions(false)
    setPredictions([])
    setSelectedFromPredictions(false)
  }

  const handleShowPredictions = (predictionsData) => {
    setPredictions(predictionsData.predictions || [])
    setShowPredictions(true)
    setPlantData(null)
    setSelectedFromPredictions(false)
  }

  const handleSelectFromPredictions = (selectedPlant) => {
    setPlantData(selectedPlant)
    setShowPredictions(false)
    setSelectedFromPredictions(true)
  }

  const handleBackToPredictions = () => {
    setShowPredictions(true)
    setSelectedFromPredictions(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌱 Plant Care Assistant</h1>
        <p>Upload a photo of your plant to get personalized care instructions</p>
      </header>

      <main className="app-main">
        {!plantData && !loading && !showPredictions && (
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

        {showPredictions && (
          <PredictionSelector
            predictions={predictions}
            onSelectPlant={handleSelectFromPredictions}
            onTakeNewPhoto={handleReset}
          />
        )}

        {plantData && !showPredictions && (
          <PlantInfo 
            plantData={plantData} 
            onReset={handleReset}
            onTryAgain={handleShowPredictions}
            onBackToPredictions={handleBackToPredictions}
            selectedFromPredictions={selectedFromPredictions}
          />
        )}
      </main>
    </div>
  )
}

export default App
