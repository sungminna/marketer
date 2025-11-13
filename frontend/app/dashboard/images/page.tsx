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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Sparkles, Loader2 } from 'lucide-react'

const imageSchema = z.object({
  provider: z.enum(['gemini', 'openai', 'imagen']),
  model: z.string().min(1, 'Model is required'),
  prompt: z.string().min(10, 'Prompt must be at least 10 characters'),
  style_preset: z.string().optional(),
  primary_color: z.string().optional(),
  secondary_color: z.string().optional(),
  aspect_ratio: z.string().optional(),
  number_of_images: z.number().min(1).max(10).optional(),
  negative_prompt: z.string().optional(),
})

type ImageFormData = z.infer<typeof imageSchema>

const providerModels = {
  gemini: ['gemini-2.5-flash-image'],
  openai: ['gpt-image-1-medium', 'gpt-image-1-high'],
  imagen: ['imagen-4-fast', 'imagen-4-standard'],
}

const stylePresets = [
  'photoreal',
  'artistic',
  'minimalist',
  'vintage',
  'modern',
  'abstract',
  'professional',
]

const aspectRatios = ['1:1', '16:9', '9:16', '4:3', '3:4']

export default function ImagesPage() {
  const [selectedProvider, setSelectedProvider] = useState<'gemini' | 'openai' | 'imagen'>('gemini')
  const [jobResult, setJobResult] = useState<any>(null)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ImageFormData>({
    resolver: zodResolver(imageSchema),
    defaultValues: {
      provider: 'gemini',
      model: 'gemini-2.5-flash-image',
      aspect_ratio: '16:9',
      number_of_images: 1,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ImageFormData) => {
      const payload = {
        provider: data.provider,
        model: data.model,
        prompt: data.prompt,
        style_preset: data.style_preset,
        design_tokens: {
          primary_color: data.primary_color,
          secondary_color: data.secondary_color,
        },
        image_config: {
          aspect_ratio: data.aspect_ratio,
          number_of_images: data.number_of_images,
        },
        negative_prompt: data.negative_prompt,
      }
      return apiClient.generateImage(payload)
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const onSubmit = (data: ImageFormData) => {
    mutation.mutate(data)
  }

  const handleProviderChange = (provider: 'gemini' | 'openai' | 'imagen') => {
    setSelectedProvider(provider)
    setValue('provider', provider)
    setValue('model', providerModels[provider][0])
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Image Generation</h1>
        <p className="text-muted-foreground">
          Create stunning AI-generated images with Gemini, OpenAI, and Imagen
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Generate Image</CardTitle>
              <CardDescription>Configure your image generation parameters</CardDescription>
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
                  {errors.model && (
                    <p className="text-sm text-red-500">{errors.model.message}</p>
                  )}
                </div>

                {/* Prompt */}
                <div className="space-y-2">
                  <Label htmlFor="prompt">Prompt</Label>
                  <Textarea
                    id="prompt"
                    placeholder="A modern tech startup office with blue and white brand colors, professional lighting, 8K resolution..."
                    rows={4}
                    {...register('prompt')}
                  />
                  {errors.prompt && (
                    <p className="text-sm text-red-500">{errors.prompt.message}</p>
                  )}
                </div>

                {/* Style Preset */}
                <div className="space-y-2">
                  <Label htmlFor="style_preset">Style Preset (Optional)</Label>
                  <select
                    id="style_preset"
                    {...register('style_preset')}
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    <option value="">None</option>
                    {stylePresets.map((style) => (
                      <option key={style} value={style}>
                        {style.charAt(0).toUpperCase() + style.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Design Tokens */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="primary_color">Primary Color</Label>
                    <Input
                      id="primary_color"
                      type="color"
                      {...register('primary_color')}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="secondary_color">Secondary Color</Label>
                    <Input
                      id="secondary_color"
                      type="color"
                      {...register('secondary_color')}
                      className="h-10"
                    />
                  </div>
                </div>

                {/* Image Config */}
                <div className="grid grid-cols-2 gap-4">
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
                  <div className="space-y-2">
                    <Label htmlFor="number_of_images">Number of Images</Label>
                    <Input
                      id="number_of_images"
                      type="number"
                      min="1"
                      max="10"
                      {...register('number_of_images', { valueAsNumber: true })}
                    />
                  </div>
                </div>

                {/* Negative Prompt */}
                <div className="space-y-2">
                  <Label htmlFor="negative_prompt">Negative Prompt (Optional)</Label>
                  <Textarea
                    id="negative_prompt"
                    placeholder="blurry, low quality, distorted..."
                    rows={2}
                    {...register('negative_prompt')}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={mutation.isPending}
                >
                  {mutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Generate Image
                    </>
                  )}
                </Button>

                {mutation.isError && (
                  <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                    {(mutation.error as any)?.response?.data?.detail ||
                      'Failed to generate image. Please try again.'}
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
                    <span className="text-sm">${jobResult.cost.toFixed(4)}</span>
                  </div>
                  {jobResult.result_url && (
                    <div className="space-y-2">
                      <span className="text-sm font-medium">Result</span>
                      <img
                        src={jobResult.result_url}
                        alt="Generated"
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
