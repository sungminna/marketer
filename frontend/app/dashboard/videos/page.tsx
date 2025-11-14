'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileUpload } from '@/components/ui/file-upload'
import { Sparkles, Loader2, ImageIcon, Scissors } from 'lucide-react'

const videoSchema = z.object({
  provider: z.enum(['veo', 'sora']),
  model: z.string().min(1, 'Model is required'),
  prompt: z.string().min(10, 'Prompt must be at least 10 characters'),
  length: z.number().min(1).max(30).optional(),
  resolution: z.string().optional(),
  aspect_ratio: z.string().optional(),
  camera_movement: z.string().optional(),
  shot_type: z.string().optional(),
  lighting: z.string().optional(),
})

const fromImageSchema = z.object({
  provider: z.enum(['veo', 'sora']),
  model: z.string().min(1, 'Model is required'),
  prompt: z.string().min(10, 'Prompt must be at least 10 characters'),
  length: z.number().min(1).max(30).optional(),
  resolution: z.string().optional(),
})

const removeBgSchema = z.object({
  provider: z.enum(['unscreen']),
  model: z.string().min(1, 'Model is required'),
})

type VideoFormData = z.infer<typeof videoSchema>
type FromImageFormData = z.infer<typeof fromImageSchema>
type RemoveBgFormData = z.infer<typeof removeBgSchema>

const providerModels = {
  veo: ['veo-3.1-fast-generate-preview-001', 'veo-3.1-standard-generate-001'],
  sora: ['sora-2-720p', 'sora-2-1080p'],
}

const resolutions = ['720p', '1080p', '4k']
const aspectRatios = ['16:9', '9:16', '1:1', '4:3']
const cameraMovements = ['pan', 'tilt', 'zoom', 'dolly', 'static']
const shotTypes = ['closeup', 'medium', 'wide', 'extreme-wide']
const lightingOptions = ['natural', 'studio', 'dramatic', 'soft', 'hard']

export default function VideosPage() {
  const [selectedProvider, setSelectedProvider] = useState<'veo' | 'sora'>('veo')
  const [jobResult, setJobResult] = useState<any>(null)
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [uploadedVideo, setUploadedVideo] = useState<File | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<VideoFormData>({
    resolver: zodResolver(videoSchema),
    defaultValues: {
      provider: 'veo',
      model: 'veo-3.1-fast-generate-preview-001',
      length: 8,
      resolution: '720p',
      aspect_ratio: '16:9',
    },
  })

  const {
    register: registerFromImage,
    handleSubmit: handleSubmitFromImage,
    setValue: setValueFromImage,
    formState: { errors: errorsFromImage },
  } = useForm<FromImageFormData>({
    resolver: zodResolver(fromImageSchema),
    defaultValues: {
      provider: 'veo',
      model: 'veo-3.1-fast-generate-preview-001',
      length: 8,
      resolution: '720p',
    },
  })

  const {
    register: registerRemoveBg,
    handleSubmit: handleSubmitRemoveBg,
    formState: { errors: errorsRemoveBg },
  } = useForm<RemoveBgFormData>({
    resolver: zodResolver(removeBgSchema),
    defaultValues: {
      provider: 'unscreen',
      model: 'unscreen-api',
    },
  })

  const mutation = useMutation({
    mutationFn: (data: VideoFormData) => {
      const payload = {
        provider: data.provider,
        model: data.model,
        prompt: data.prompt,
        video_config: {
          length: data.length,
          resolution: data.resolution,
          aspect_ratio: data.aspect_ratio,
        },
        cinematography: {
          camera_movement: data.camera_movement,
          shot_type: data.shot_type,
          lighting: data.lighting,
        },
      }
      return apiClient.generateVideo(payload)
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const fromImageMutation = useMutation({
    mutationFn: async (data: FromImageFormData) => {
      if (!uploadedImage) throw new Error('Please upload an image first')

      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(uploadedImage)
      })

      const payload = {
        provider: data.provider,
        model: data.model,
        prompt: data.prompt,
        source_image: base64,
        video_config: {
          length: data.length,
          resolution: data.resolution,
        },
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/videos/from-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error('Failed to generate video from image')
      return response.json()
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const removeBgMutation = useMutation({
    mutationFn: async (data: RemoveBgFormData) => {
      if (!uploadedVideo) throw new Error('Please upload a video first')

      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(uploadedVideo)
      })

      const payload = {
        provider: data.provider,
        model: data.model,
        source_video: base64,
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/videos/remove-background`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error('Failed to remove background')
      return response.json()
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const onSubmit = (data: VideoFormData) => {
    mutation.mutate(data)
  }

  const onSubmitFromImage = (data: FromImageFormData) => {
    fromImageMutation.mutate(data)
  }

  const onSubmitRemoveBg = (data: RemoveBgFormData) => {
    removeBgMutation.mutate(data)
  }

  const handleProviderChange = (provider: 'veo' | 'sora') => {
    setSelectedProvider(provider)
    setValue('provider', provider)
    setValue('model', providerModels[provider][0])
    setValueFromImage('provider', provider)
    setValueFromImage('model', providerModels[provider][0])
  }

  // Check for template data on mount
  useEffect(() => {
    const templateDataStr = sessionStorage.getItem('templateData')
    if (templateDataStr) {
      try {
        const templateData = JSON.parse(templateDataStr)

        // Only apply if this is a video template
        if (templateData.template_type === 'video' && templateData.config) {
          const config = templateData.config

          // Pre-fill the generate form with template config
          if (config.provider) {
            handleProviderChange(config.provider)
          }
          if (config.prompt) {
            setValue('prompt', config.prompt)
          }
          if (config.video_config?.length) {
            setValue('length', config.video_config.length)
          }
          if (config.video_config?.resolution) {
            setValue('resolution', config.video_config.resolution)
          }
          if (config.video_config?.aspect_ratio) {
            setValue('aspect_ratio', config.video_config.aspect_ratio)
          }
          if (config.cinematography?.camera_movement) {
            setValue('camera_movement', config.cinematography.camera_movement)
          }
          if (config.cinematography?.shot_type) {
            setValue('shot_type', config.cinematography.shot_type)
          }
          if (config.cinematography?.lighting) {
            setValue('lighting', config.cinematography.lighting)
          }
        }

        // Clear the template data after using it
        sessionStorage.removeItem('templateData')
      } catch (error) {
        console.error('Failed to load template data:', error)
      }
    }
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Video Generation</h1>
        <p className="text-muted-foreground">
          Create stunning AI-generated videos with Veo and Sora
        </p>
      </div>

      <Tabs defaultValue="generate" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generate">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate
          </TabsTrigger>
          <TabsTrigger value="from-image">
            <ImageIcon className="w-4 h-4 mr-2" />
            From Image
          </TabsTrigger>
          <TabsTrigger value="remove-bg">
            <Scissors className="w-4 h-4 mr-2" />
            Remove Background
          </TabsTrigger>
        </TabsList>

        {/* GENERATE TAB */}
        <TabsContent value="generate">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Generate Video</CardTitle>
                  <CardDescription>Configure your video generation parameters</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Provider Selection */}
                <div className="space-y-2">
                  <Label>Provider</Label>
                  <div className="flex gap-2">
                    {Object.keys(providerModels).map((provider) => (
                      <Button
                        key={provider}
                        type="button"
                        variant={selectedProvider === provider ? 'default' : 'outline'}
                        onClick={() => handleProviderChange(provider as any)}
                        className="flex-1"
                      >
                        {provider.charAt(0).toUpperCase() + provider.slice(1)}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Model Selection */}
                <div className="space-y-2">
                  <Label htmlFor="model">Model</Label>
                  <select
                    id="model"
                    {...register('model')}
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    {providerModels[selectedProvider].map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Prompt */}
                <div className="space-y-2">
                  <Label htmlFor="prompt">Prompt</Label>
                  <Textarea
                    id="prompt"
                    placeholder="A product showcase video with smooth camera movement, professional lighting, modern aesthetic..."
                    rows={4}
                    {...register('prompt')}
                  />
                  {errors.prompt && (
                    <p className="text-sm text-red-500">{errors.prompt.message}</p>
                  )}
                </div>

                {/* Video Config */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="length">Length (seconds)</Label>
                    <Input
                      id="length"
                      type="number"
                      min="1"
                      max="30"
                      {...register('length', { valueAsNumber: true })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="resolution">Resolution</Label>
                    <select
                      id="resolution"
                      {...register('resolution')}
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    >
                      {resolutions.map((res) => (
                        <option key={res} value={res}>
                          {res}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="aspect_ratio">Aspect Ratio</Label>
                    <select
                      id="aspect_ratio"
                      {...register('aspect_ratio')}
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    >
                      {aspectRatios.map((ratio) => (
                        <option key={ratio} value={ratio}>
                          {ratio}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Cinematography */}
                <div className="space-y-4">
                  <h3 className="text-sm font-medium">Cinematography (Optional)</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="camera_movement">Camera Movement</Label>
                      <select
                        id="camera_movement"
                        {...register('camera_movement')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        <option value="">None</option>
                        {cameraMovements.map((movement) => (
                          <option key={movement} value={movement}>
                            {movement.charAt(0).toUpperCase() + movement.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="shot_type">Shot Type</Label>
                      <select
                        id="shot_type"
                        {...register('shot_type')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        <option value="">None</option>
                        {shotTypes.map((type) => (
                          <option key={type} value={type}>
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="lighting">Lighting</Label>
                      <select
                        id="lighting"
                        {...register('lighting')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        <option value="">None</option>
                        {lightingOptions.map((light) => (
                          <option key={light} value={light}>
                            {light.charAt(0).toUpperCase() + light.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                <Button type="submit" className="w-full" disabled={mutation.isPending}>
                  {mutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Generate Video
                    </>
                  )}
                </Button>

                {mutation.isError && (
                  <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                    {(mutation.error as any)?.response?.data?.detail ||
                      'Failed to generate video. Please try again.'}
                  </div>
                )}
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Result Panel */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Result</CardTitle>
                  <CardDescription>Your generation job status</CardDescription>
                </CardHeader>
                <CardContent>
                  {jobResult ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Job ID</span>
                        <span className="text-xs font-mono">{jobResult.id}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Status</span>
                        <Badge
                          variant={
                            jobResult.status === 'completed'
                              ? 'success'
                              : jobResult.status === 'failed'
                              ? 'destructive'
                              : 'secondary'
                          }
                        >
                          {jobResult.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Cost</span>
                        <span className="text-sm">${jobResult.cost.toFixed(2)}</span>
                      </div>
                      {jobResult.result_url && (
                        <div className="space-y-2">
                          <span className="text-sm font-medium">Result</span>
                          <video
                            src={jobResult.result_url}
                            controls
                            className="w-full rounded-lg border"
                          />
                        </div>
                      )}
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => window.open(`/dashboard/jobs/${jobResult.id}`, '_blank')}
                      >
                        View Job Details
                      </Button>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      Submit a generation request to see results
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* FROM IMAGE TAB */}
        <TabsContent value="from-image">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Convert Image to Video</CardTitle>
                  <CardDescription>Upload an image and generate an animated video</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitFromImage(onSubmitFromImage)} className="space-y-6">
                    {/* File Upload */}
                    <div className="space-y-2">
                      <Label>Source Image</Label>
                      <FileUpload
                        accept="image/*"
                        onChange={setUploadedImage}
                        value={uploadedImage}
                        maxSize={10}
                      />
                    </div>

                    {/* Provider Selection */}
                    <div className="space-y-2">
                      <Label>Provider</Label>
                      <div className="flex gap-2">
                        {Object.keys(providerModels).map((provider) => (
                          <Button
                            key={provider}
                            type="button"
                            variant={selectedProvider === provider ? 'default' : 'outline'}
                            onClick={() => handleProviderChange(provider as any)}
                            className="flex-1"
                          >
                            {provider.charAt(0).toUpperCase() + provider.slice(1)}
                          </Button>
                        ))}
                      </div>
                    </div>

                    {/* Model Selection */}
                    <div className="space-y-2">
                      <Label htmlFor="model-from-image">Model</Label>
                      <select
                        id="model-from-image"
                        {...registerFromImage('model')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        {providerModels[selectedProvider].map((model) => (
                          <option key={model} value={model}>
                            {model}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Prompt */}
                    <div className="space-y-2">
                      <Label htmlFor="prompt-from-image">Prompt</Label>
                      <Textarea
                        id="prompt-from-image"
                        placeholder="Describe how you want to animate this image..."
                        rows={3}
                        {...registerFromImage('prompt')}
                      />
                      {errorsFromImage.prompt && (
                        <p className="text-sm text-red-500">{errorsFromImage.prompt.message}</p>
                      )}
                    </div>

                    {/* Video Config */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="length-from-image">Length (seconds)</Label>
                        <Input
                          id="length-from-image"
                          type="number"
                          min="1"
                          max="30"
                          {...registerFromImage('length', { valueAsNumber: true })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="resolution-from-image">Resolution</Label>
                        <select
                          id="resolution-from-image"
                          {...registerFromImage('resolution')}
                          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                        >
                          {resolutions.map((res) => (
                            <option key={res} value={res}>
                              {res}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <Button type="submit" className="w-full" disabled={fromImageMutation.isPending}>
                      {fromImageMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Converting...
                        </>
                      ) : (
                        <>
                          <ImageIcon className="mr-2 h-4 w-4" />
                          Convert to Video
                        </>
                      )}
                    </Button>

                    {fromImageMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(fromImageMutation.error as any)?.message ||
                          'Failed to convert image. Please try again.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Result Panel */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Result</CardTitle>
                  <CardDescription>Your conversion job status</CardDescription>
                </CardHeader>
                <CardContent>
                  {jobResult ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Job ID</span>
                        <span className="text-xs font-mono">{jobResult.id}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Status</span>
                        <Badge
                          variant={
                            jobResult.status === 'completed'
                              ? 'success'
                              : jobResult.status === 'failed'
                              ? 'destructive'
                              : 'secondary'
                          }
                        >
                          {jobResult.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Cost</span>
                        <span className="text-sm">${jobResult.cost.toFixed(2)}</span>
                      </div>
                      {jobResult.result_url && (
                        <div className="space-y-2">
                          <span className="text-sm font-medium">Result</span>
                          <video
                            src={jobResult.result_url}
                            controls
                            className="w-full rounded-lg border"
                          />
                        </div>
                      )}
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => window.open(`/dashboard/jobs/${jobResult.id}`, '_blank')}
                      >
                        View Job Details
                      </Button>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      Submit a conversion request to see results
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* REMOVE BACKGROUND TAB */}
        <TabsContent value="remove-bg">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Remove Video Background</CardTitle>
                  <CardDescription>Upload a video to remove its background</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitRemoveBg(onSubmitRemoveBg)} className="space-y-6">
                    {/* File Upload */}
                    <div className="space-y-2">
                      <Label>Source Video</Label>
                      <FileUpload
                        accept="video/*"
                        onChange={setUploadedVideo}
                        value={uploadedVideo}
                        maxSize={100}
                      />
                    </div>

                    {/* Provider (Fixed to Unscreen) */}
                    <div className="space-y-2">
                      <Label>Provider</Label>
                      <Input value="Unscreen" disabled className="bg-muted" />
                      <p className="text-xs text-muted-foreground">
                        Background removal is powered by Unscreen
                      </p>
                    </div>

                    <Button type="submit" className="w-full" disabled={removeBgMutation.isPending}>
                      {removeBgMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Removing Background...
                        </>
                      ) : (
                        <>
                          <Scissors className="mr-2 h-4 w-4" />
                          Remove Background
                        </>
                      )}
                    </Button>

                    {removeBgMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(removeBgMutation.error as any)?.message ||
                          'Failed to remove background. Please try again.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Result Panel */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Result</CardTitle>
                  <CardDescription>Your background removal job status</CardDescription>
                </CardHeader>
                <CardContent>
                  {jobResult ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Job ID</span>
                        <span className="text-xs font-mono">{jobResult.id}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Status</span>
                        <Badge
                          variant={
                            jobResult.status === 'completed'
                              ? 'success'
                              : jobResult.status === 'failed'
                              ? 'destructive'
                              : 'secondary'
                          }
                        >
                          {jobResult.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Cost</span>
                        <span className="text-sm">${jobResult.cost.toFixed(2)}</span>
                      </div>
                      {jobResult.result_url && (
                        <div className="space-y-2">
                          <span className="text-sm font-medium">Result</span>
                          <video
                            src={jobResult.result_url}
                            controls
                            className="w-full rounded-lg border"
                          />
                        </div>
                      )}
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => window.open(`/dashboard/jobs/${jobResult.id}`, '_blank')}
                      >
                        View Job Details
                      </Button>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      Submit a background removal request to see results
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
