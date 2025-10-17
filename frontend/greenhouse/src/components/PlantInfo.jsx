import { useState, useEffect } from 'react'
import { getPlantImage } from '../services/plantDataService'

const PlantInfo = ({ plantData, onReset }) => {
  const { name, care, url, confidence } = plantData
  const [plantImage, setPlantImage] = useState(null)
  const [imageLoading, setImageLoading] = useState(true)

  // Fetch plant image when component mounts
  useEffect(() => {
    const fetchImage = async () => {
      if (name) {
        setImageLoading(true)
        try {
          const imageData = await getPlantImage(name)
          setPlantImage(imageData)
        } catch (error) {
          console.error('PlantInfo: Error loading plant image:', error)
        } finally {
          setImageLoading(false)
        }
      }
    }

    fetchImage()
  }, [name])

  const careItems = [
    { icon: '☀️', title: 'Light Requirements', content: care.light_requirements },
    { icon: '💧', title: 'Watering Needs', content: care.watering_needs },
    { icon: '🌱', title: 'Soil Preferences', content: care.soil_preferences },
    { icon: '🌡️', title: 'Temperature & Humidity', content: care.temperature_humidity },
    { icon: '🍃', title: 'Fertilization', content: care.fertilization },
    { icon: '✂️', title: 'Pruning & Maintenance', content: care.pruning_maintenance }
  ].filter(item => item.content) // Only show items with content

  return (
    <div className="plant-info">
      <div className="plant-header">
        <div className="plant-title-section">
          <h2>🌿 {name}</h2>
          {plantImage && !imageLoading && (
            <div className="plant-image-container">
              <img 
                src={plantImage.url} 
                alt={`${name} plant`}
                className="plant-reference-image"
                onError={(e) => {
                  console.error(`Failed to load image: ${plantImage.url}`)
                  e.target.style.display = 'none'
                }}
              />
            </div>
          )}
          {imageLoading && (
            <div className="image-loading">🔍 Loading plant image...</div>
          )}
          {!plantImage && !imageLoading && (
            <div className="image-loading">📷 No reference image available</div>
          )}
        </div>
        <div className="header-actions">
          <span className="ai-badge">
            🤖 AI Identified
            {confidence && ` (${(confidence * 100).toFixed(1)}% confidence)`}
          </span>
          <button onClick={onReset} className="new-search-btn">
            Upload New Photo
          </button>
        </div>
      </div>

      <div className="care-grid">
        {careItems.map((item, index) => (
          <div key={index} className="care-card">
            <div className="care-header">
              <span className="care-icon">{item.icon}</span>
              <h3>{item.title}</h3>
            </div>
            <p className="care-content">{item.content}</p>
          </div>
        ))}
      </div>

      {careItems.length === 0 && (
        <div className="no-care-data">
          <p>🌱 Plant identified but detailed care instructions are being added soon!</p>
        </div>
      )}

      {url && (
        <div className="additional-info">
          <a 
            href={url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="learn-more-btn"
          >
            Learn More About {name} 🔗
          </a>
        </div>
      )}
    </div>
  )
}

export default PlantInfo