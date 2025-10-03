import { useState, useRef } from 'react'
import { identifyPlantWithCNN } from '../services/plantIdentification'
import { getPlantCareData } from '../services/plantDataService'

const ImageUpload = ({ onPlantIdentified, onError, onLoadingChange }) => {
  const [dragActive, setDragActive] = useState(false)
  const [preview, setPreview] = useState(null)
  const fileInputRef = useRef(null)

  const handleFiles = async (files) => {
    const file = files[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      onError('Please upload an image file')
      return
    }

    // Validate file size (10MB limit for CNN model)
    if (file.size > 10 * 1024 * 1024) {
      onError('File size must be less than 10MB')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(file)

    try {
      onLoadingChange(true)
      
      // Use your CNN model for plant identification
      const plantName = await identifyPlantWithCNN(file)
      
      // Get care data from your JSON
      const careData = getPlantCareData(plantName)
      
      if (careData) {
        onPlantIdentified(careData)
      } else {
        onError(`Plant identified as "${plantName}" but no care data available yet.`)
      }
    } catch (error) {
      console.error('Plant identification error:', error)
      onError('Failed to identify plant. Please try again with a clearer image.')
    } finally {
      onLoadingChange(false)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }

  const onButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="upload-container">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          accept="image/*"
          onChange={handleChange}
        />
        
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Plant preview" className="preview-image" />
            <p>Click to change image or drag a new one</p>
            <small>CNN model will analyze this image</small>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">🔬</div>
            <h3>Drop your plant photo here</h3>
            <p>Our CNN model will identify it</p>
            <small>Supports: JPG, PNG, WebP (max 10MB)</small>
          </div>
        )}
      </div>
    </div>
  )
}

export default ImageUpload