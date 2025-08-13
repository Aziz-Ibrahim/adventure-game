function LoadingStatus({}){
    return <div className="loading-container">
        <h2>
            Generating Your {theme} Story
        </h2>
        <div className="loading-animation">
            <div className="spinner"></div>
        </div>

        <p className="loading-info">
            Please wait for your story to generate
        </p>
    </div>
}

export default LoadingStatus;