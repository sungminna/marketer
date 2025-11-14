'use client'

import { useCallback, useState } from 'react'
import { cn } from '@/lib/utils'
import { Upload, X, File, Image as ImageIcon, Video } from 'lucide-react'
import { Button } from './button'

interface FileUploadProps {
  accept?: string
  onChange: (file: File | null) => void
  value?: File | null
  className?: string
  maxSize?: number // in MB
  preview?: boolean
}

export function FileUpload({
  accept = 'image/*',
  onChange,
  value,
  className,
  maxSize = 10,
  preview = true,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(
    (file: File) => {
      setError(null)

      // Check file size
      if (file.size > maxSize * 1024 * 1024) {
        setError(`File size must be less than ${maxSize}MB`)
        return
      }

      // Check file type
      const acceptedTypes = accept.split(',').map((t) => t.trim())
      const fileType = file.type
      const isAccepted = acceptedTypes.some((type) => {
        if (type.endsWith('/*')) {
          return fileType.startsWith(type.replace('/*', ''))
        }
        return fileType === type
      })

      if (!isAccepted) {
        setError('Invalid file type')
        return
      }

      onChange(file)

      // Generate preview
      if (preview && file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setPreviewUrl(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      } else if (preview && file.type.startsWith('video/')) {
        const url = URL.createObjectURL(file)
        setPreviewUrl(url)
      }
    },
    [accept, maxSize, onChange, preview]
  )

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setDragActive(false)

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0])
      }
    },
    [handleFile]
  )

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0])
      }
    },
    [handleFile]
  )

  const handleRemove = useCallback(() => {
    onChange(null)
    setPreviewUrl(null)
    setError(null)
  }, [onChange])

  const getIcon = () => {
    if (accept.startsWith('image/')) return <ImageIcon className="w-8 h-8" />
    if (accept.startsWith('video/')) return <Video className="w-8 h-8" />
    return <File className="w-8 h-8" />
  }

  if (value && previewUrl) {
    return (
      <div className={cn('relative', className)}>
        {value.type.startsWith('image/') ? (
          <div className="relative border-2 border-dashed rounded-lg overflow-hidden">
            <img src={previewUrl} alt="Preview" className="w-full h-48 object-cover" />
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2"
              onClick={handleRemove}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : value.type.startsWith('video/') ? (
          <div className="relative border-2 border-dashed rounded-lg overflow-hidden">
            <video src={previewUrl} className="w-full h-48 object-cover" controls />
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2"
              onClick={handleRemove}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : (
          <div className="flex items-center justify-between p-4 border-2 border-dashed rounded-lg">
            <div className="flex items-center space-x-3">
              <File className="w-6 h-6 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">{value.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(value.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <Button type="button" variant="ghost" size="icon" onClick={handleRemove}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={className}>
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          dragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50',
          error && 'border-red-500'
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept={accept}
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center space-y-4">
          <div className="text-muted-foreground">{getIcon()}</div>
          <div>
            <p className="text-sm font-medium">
              <span className="text-primary">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {accept.replace(/\*/g, 'all')} (max {maxSize}MB)
            </p>
          </div>
          <Upload className="w-4 h-4 text-muted-foreground" />
        </div>
      </div>
      {error && <p className="text-sm text-red-500 mt-2">{error}</p>}
    </div>
  )
}
