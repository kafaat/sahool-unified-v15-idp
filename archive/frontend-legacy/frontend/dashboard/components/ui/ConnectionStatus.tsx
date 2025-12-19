'use client'

import { useEffect, useState } from 'react'

export function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const [showStatus, setShowStatus] = useState(false)

  useEffect(() => {
    // Check initial status
    setIsOnline(navigator.onLine)

    const handleOnline = () => {
      setIsOnline(true)
      setShowStatus(true)
      // Hide after 3 seconds when back online
      setTimeout(() => setShowStatus(false), 3000)
    }

    const handleOffline = () => {
      setIsOnline(false)
      setShowStatus(true)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Show offline status initially if offline
    if (!navigator.onLine) {
      setShowStatus(true)
    }

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (!showStatus) return null

  return (
    <div
      className={`connection-status ${
        isOnline ? 'connection-online' : 'connection-offline'
      }`}
    >
      <span
        className={`w-2 h-2 rounded-full ${
          isOnline ? 'bg-white' : 'bg-white animate-pulse'
        }`}
      />
      {isOnline ? 'متصل بالإنترنت' : 'غير متصل - العمل بدون اتصال'}
    </div>
  )
}
