import { useState, useEffect } from 'react'
import { getPlantImage } from '../services/plantDataService'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip
} from 'recharts'

const PlantInfo = ({ plantData, onReset, onTryAgain, onBackToPredictions, selectedFromPredictions }) => {
  const { name, care, url, confidence } = plantData
  const [plantImage, setPlantImage] = useState(null)
  const [imageLoading, setImageLoading] = useState(true)

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

  const getCareLevel = (careText, careType) => {
    if (!careText) return 0
    
    const text = careText.toLowerCase()
    let result = 3 
    
    switch (careType) {
      case 'light':
        if (text.includes('full sun') || text.includes('direct sunlight') || text.includes('full sunlight')) result = 5
        else if (text.includes('bright') && text.includes('indirect')) result = 3
        else if (text.includes('low light') || text.includes('tolerate low')) result = 1
        else if (text.includes('bright')) result = 4
        else if (text.includes('partial shade') || text.includes('shade')) result = 2
        break
        
      case 'water':
        if (text.includes('consistently moist') || text.includes('evenly moist')) result = 4
        else if (text.includes('dry out completely') || text.includes('drought-tolerant') || text.includes('sparingly')) result = 1
        else if (text.includes('dry out between') || text.includes('top inch')) result = 2
        else if (text.includes('regularly') && !text.includes('moist')) result = 3
        else if (text.includes('sensitive to drought') || text.includes('wilt quickly')) result = 5
        break
        
      case 'soil':
        if (text.includes('succulent') || text.includes('cactus') || text.includes('specifically designed for succulents')) result = 1
        else if (text.includes('standard potting soil') || (text.includes('well-draining') && !text.includes('rich') && !text.includes('peat') && !text.includes('bark'))) result = 2
        else if (text.includes('well-draining') && (text.includes('rich in organic') || text.includes('peat') || text.includes('pine bark'))) result = 3
        else if (text.includes('multiple components') || (text.includes('mix of') && text.includes('and') && text.includes('and'))) result = 4
        else if (text.includes('complex') || text.includes('rare components') || text.includes('special requirements')) result = 5
        break
        
      case 'humidity':
        if (text.includes('low humidity') || text.includes('average household') || text.includes('sufficient')) result = 1
        else if (text.includes('can tolerate') && text.includes('humidity')) result = 2
        else if (text.includes('moderate humidity') || text.includes('above 50%') || text.includes('above 40%')) result = 3
        else if (text.includes('misting') || text.includes('humidifier') || text.includes('humidity tray')) result = 4
        else if (text.includes('high humidity') || text.includes('above 60%') || text.includes('humid environments')) result = 5
        break
        
      case 'fertilizer':
        if (text.includes('sparingly') || text.includes('once in the spring') || text.includes('every 2-3 months')) result = 1
        else if (text.includes('every 4-6 weeks') || text.includes('monthly')) result = 2
        else if (text.includes('every 2-4 weeks') || text.includes('balanced') && text.includes('growing season')) result = 3
        else if (text.includes('weekly') || text.includes('frequent')) result = 4
        else if (text.includes('daily') || text.includes('constant feeding')) result = 5
        break
        
      case 'maintenance':
        if (text.includes('minimal') || text.includes('occasional') || text.includes('clean the leaves occasionally')) result = 1
        else if (text.includes('remove yellow') || text.includes('repot every 2-3 years')) result = 2
        else if (text.includes('trim') || text.includes('repot every 1-2 years')) result = 3
        else if (text.includes('regularly prune') || text.includes('pinch back') || text.includes('control growth')) result = 4
        else if (text.includes('daily care') || text.includes('constant attention')) result = 5
        break
    }
    
    return result
  }

  const calculateDifficulty = () => {
    const lightLevel = getCareLevel(care.light_requirements, 'light')
    const waterLevel = getCareLevel(care.watering_needs, 'water')
    const soilLevel = getCareLevel(care.soil_preferences, 'soil')
    const humidityLevel = getCareLevel(care.temperature_humidity, 'humidity')
    const fertilizerLevel = getCareLevel(care.fertilization, 'fertilizer')
    const maintenanceLevel = getCareLevel(care.pruning_maintenance, 'maintenance')
    
    const avgDifficulty = (lightLevel + waterLevel + soilLevel + humidityLevel + fertilizerLevel + maintenanceLevel) / 6
    
    if (avgDifficulty <= 1.8) return 1
    if (avgDifficulty <= 2.5) return 2
    if (avgDifficulty <= 3.3) return 3
    if (avgDifficulty <= 4.2) return 4
    return 5
  }

  const handleTryAgain = () => {
    if (plantData.predictions && plantData.predictions.length > 0) {
      onTryAgain({
        predictions: plantData.predictions,
        count: plantData.predictions.length
      })
    } else {
      console.error('No alternative predictions available')
    }
  }

  const radarData = [
    {
      aspect: 'Light Requirements',
      value: getCareLevel(care.light_requirements, 'light'),
      fullMark: 5,
      description: care.light_requirements || 'Not specified'
    },
    {
      aspect: 'Watering Needs',
      value: getCareLevel(care.watering_needs, 'water'),
      fullMark: 5,
      description: care.watering_needs || 'Not specified'
    },
    {
      aspect: 'Soil Preferences',
      value: getCareLevel(care.soil_preferences, 'soil'),
      fullMark: 5,
      description: care.soil_preferences || 'Not specified'
    },
    {
      aspect: 'Temperature & Humidity',
      value: getCareLevel(care.temperature_humidity, 'humidity'),
      fullMark: 5,
      description: care.temperature_humidity || 'Not specified'
    },
    {
      aspect: 'Fertilization',
      value: getCareLevel(care.fertilization, 'fertilizer'),
      fullMark: 5,
      description: care.fertilization || 'Not specified'
    },
    {
      aspect: 'Pruning & Maintenance',
      value: getCareLevel(care.pruning_maintenance, 'maintenance'),
      fullMark: 5,
      description: care.pruning_maintenance || 'Not specified'
    }
  ]

  const difficultyLevel = calculateDifficulty()

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{data.aspect}</p>
          <p className="tooltip-value">Level: {data.value}/5</p>
          <p className="tooltip-description">{data.description}</p>
        </div>
      )
    }
    return null
  }

  const careItems = [
    { icon: '☀️', title: 'Light Requirements', content: care.light_requirements },
    { icon: '💧', title: 'Watering Needs', content: care.watering_needs },
    { icon: '🌱', title: 'Soil Preferences', content: care.soil_preferences },
    { icon: '🌡️', title: 'Temperature & Humidity', content: care.temperature_humidity },
    { icon: '🍃', title: 'Fertilization', content: care.fertilization },
    { icon: '✂️', title: 'Pruning & Maintenance', content: care.pruning_maintenance }
  ].filter(item => item.content)

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
          <div className="action-buttons">
            {selectedFromPredictions ? (
              <button 
                onClick={onBackToPredictions} 
                className="try-again-btn"
              >
                ← Back
              </button>
            ) : (
              <button 
                onClick={handleTryAgain} 
                className="try-again-btn"
                disabled={!plantData.predictions || plantData.predictions.length === 0}
              >
                🤔 Try Again
              </button>
            )}
            <button onClick={onReset} className="new-search-btn">
              📷 Upload New Photo
            </button>
          </div>
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

      <div className="care-analytics-section">
        <div className="radar-chart-container">
          <h4>Plant Care Requirements Analysis</h4>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
                <PolarGrid />
                <PolarAngleAxis dataKey="aspect" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis 
                  angle={0} 
                  domain={[0, 5]} 
                  tick={{ fontSize: 9 }}
                  tickCount={6}
                />
                <Radar
                  name={name}
                  dataKey="value"
                  stroke="#4CAF50"
                  fill="#4CAF50"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="difficulty-assessment">
          <h4>Care Difficulty</h4>
          <div className="difficulty-card">
            <div className="difficulty-level">
              <span className="difficulty-score-large">{difficultyLevel}/5</span>
            </div>
            <p className="difficulty-explanation">
              Computed as the mean of six care parameter assessments (1-5 scale).
            </p>
          </div>
        </div>
      </div>

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