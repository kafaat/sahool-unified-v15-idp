'use client'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'rectangular' | 'circular'
  width?: string | number
  height?: string | number
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
}: SkeletonProps) {
  const baseStyles = 'skeleton'
  const variantStyles = {
    text: 'h-4 rounded',
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
  }

  const style: React.CSSProperties = {
    width: width || '100%',
    height: height || (variant === 'text' ? '1rem' : '100%'),
  }

  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      style={style}
    />
  )
}

// Pre-built skeleton components
export function SkeletonCard() {
  return (
    <div className="card rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton width={80} height={12} variant="text" />
          <Skeleton width={60} height={24} variant="text" />
        </div>
        <Skeleton width={40} height={40} variant="circular" />
      </div>
      <Skeleton width={100} height={12} variant="text" />
    </div>
  )
}

export function SkeletonTaskItem() {
  return (
    <div className="card rounded-lg p-3 border-r-4 border-gray-300 space-y-2">
      <div className="flex justify-between items-start">
        <Skeleton width="60%" height={16} variant="text" />
        <Skeleton width={60} height={20} variant="rectangular" />
      </div>
      <Skeleton width="40%" height={12} variant="text" />
      <div className="flex justify-between items-center">
        <Skeleton width={80} height={12} variant="text" />
        <Skeleton width={24} height={24} variant="circular" />
      </div>
    </div>
  )
}

export function SkeletonEventItem() {
  return (
    <div className="card rounded-lg p-3 border space-y-2">
      <div className="flex items-center gap-2">
        <Skeleton width={24} height={24} variant="circular" />
        <Skeleton width="50%" height={14} variant="text" />
      </div>
      <Skeleton width="80%" height={12} variant="text" />
      <Skeleton width={60} height={10} variant="text" />
    </div>
  )
}

export function SkeletonStats() {
  return (
    <div className="grid grid-cols-6 gap-4">
      {[...Array(6)].map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  )
}
