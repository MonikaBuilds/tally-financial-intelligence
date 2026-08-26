import { useEffect, useState } from 'react'
import { apiGet } from '../api/client'

export function useFetch(path) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false

    setLoading(true)
    setError(null)

    apiGet(path)
      .then((result) => {
        if (!ignore) setData(result)
      })
      .catch((err) => {
        if (!ignore) setError(err.message)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [path])

  return { data, loading, error }
}
