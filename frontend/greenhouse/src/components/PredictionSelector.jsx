import { useState, useEffect } from 'react'
import { getPlantImage } from '../services/plantDataService'

const PredictionSelector = ({ predictions, onSelectPlant, onTakeNewPhoto }) => {
  const [plantImages, setPlantImages] = useState({})
  const [loadingImages, setLoadingImages] = useState(true)

  useEffect(() => {
    const fetchImages = async () => {
      setLoadingImages(true)
      const imagePromises = predictions.map(async (prediction) => {
        try {
          const imageData = await getPlantImage(prediction.name)
          return [prediction.name, imageData]
        } catch (error) {
          console.error(`Error loading image for ${prediction.name}:`, error)
          return [prediction.name, null]
        }
      })

      const imageResults = await Promise.all(imagePromises)
      const imageMap = Object.fromEntries(imageResults)
      setPlantImages(imageMap)
      setLoadingImages(false)
    }

    if (predictions && predictions.length > 0) {
      fetchImages()
    }
  }, [predictions])

  const handlePlantSelect = (prediction) => {
    onSelectPlant({
      name: prediction.name,
      care: prediction.care,
      url: prediction.url,
      confidence: prediction.confidence
    })
  }

  return (
    <div className="prediction-selector">
      <div className="prediction-header">
        <h2>🤔 Not quite right? Choose from our top predictions:</h2>
        <p>Select the plant that matches your photo, or take a new picture if none match.</p>
      </div>

      <div className="predictions-grid">
        {predictions.map((prediction, index) => (
          <div key={index} className="prediction-card" onClick={() => handlePlantSelect(prediction)}>
            <div className="prediction-image-container">
              {loadingImages ? (
                <div className="prediction-image-loading">🔍</div>
              ) : plantImages[prediction.name] ? (
                <img 
                  src={plantImages[prediction.name].url}
                  alt={`${prediction.name} plant`}
                  className="prediction-image"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    e.target.nextSibling.style.display = 'block'
                  }}
                />
              ) : null}
              <div className="prediction-image-fallback" style={{display: 'none'}}>
                🌱
              </div>
            </div>
            
            <div className="prediction-info">
              <h3 className="prediction-name">{prediction.name}</h3>
              <div className="prediction-confidence">
                <span className="confidence-bar">
                  <span 
                    className="confidence-fill" 
                    style={{width: `${prediction.confidence * 100}%`}}
                  ></span>
                </span>
                <span className="confidence-text">
                  {(prediction.confidence * 100).toFixed(1)}% confidence
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="prediction-actions">
        <button onClick={onTakeNewPhoto} className="new-photo-btn">
          📷 Take New Photo
        </button>
      </div>

      <div className="not-in-list-message">
        <p>🚫 Don't see your plant in the list? <strong>Take a new photo</strong> with better lighting or a clearer view of the leaves and stem.</p>
      </div>
    </div>
  )
}

export default PredictionSelector