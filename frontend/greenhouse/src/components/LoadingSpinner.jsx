const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner">
        <div className="leaf leaf1">🌿</div>
        <div className="leaf leaf2">🌱</div>
        <div className="leaf leaf3">🍃</div>
      </div>
      <h3>🔬 CNN Model analyzing your plant...</h3>
      <p>Advanced neural network processing in progress</p>
      <div className="progress-steps">
        <div className="step">📸 Image preprocessing</div>
        <div className="step">🧠 Feature extraction</div>
        <div className="step">🔍 Plant classification</div>
      </div>
    </div>
  )
}

export default LoadingSpinner