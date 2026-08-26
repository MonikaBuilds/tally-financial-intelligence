function ErrorMessage({ message }) {
  return (
    <div className="error-message">
      Something went wrong{message ? `: ${message}` : '.'}
    </div>
  )
}

export default ErrorMessage
