'use client'

import { useState } from 'react'
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
import { Sparkles, Loader2 } from 'lucide-react'

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

type VideoFormData = z.infer<typeof videoSchema>

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

  const onSubmit = (data: VideoFormData) => {
    mutation.mutate(data)
  }

  const handleProviderChange = (provider: 'veo' | 'sora') => {
    setSelectedProvider(provider)
    setValue('provider', provider)
    setValue('model', providerModels[provider][0])
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Video Generation</h1>
        <p className="text-muted-foreground">
          Create stunning AI-generated videos with Veo and Sora
        </p>
      </div>

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
    </div>
  )
}
