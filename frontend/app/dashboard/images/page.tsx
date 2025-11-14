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
import { Sparkles, Loader2, Wand2, Layout } from 'lucide-react'

// Generate schema
const generateSchema = z.object({
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

// Edit schema
const editSchema = z.object({
  provider: z.enum(['gemini', 'openai', 'imagen']),
  model: z.string().min(1, 'Model is required'),
  prompt: z.string().min(5, 'Prompt is required'),
  edit_type: z.enum(['style_transfer', 'pose_change', 'color_adjustment', 'background_replacement']),
})

// Prototype schema
const prototypeSchema = z.object({
  provider: z.enum(['gemini', 'openai', 'imagen']),
  model: z.string().min(1, 'Model is required'),
  prompt: z.string().min(10, 'Prompt is required'),
  prototype_type: z.enum(['app_screen', 'icon', 'logo', 'banner']),
  platform: z.string().optional(),
})

type GenerateFormData = z.infer<typeof generateSchema>
type EditFormData = z.infer<typeof editSchema>
type PrototypeFormData = z.infer<typeof prototypeSchema>

const providerModels = {
  gemini: ['gemini-2.5-flash-image'],
  openai: ['gpt-image-1-medium', 'gpt-image-1-high'],
  imagen: ['imagen-4-fast', 'imagen-4-standard'],
}

const stylePresets = ['photoreal', 'artistic', 'minimalist', 'vintage', 'modern', 'abstract', 'professional']
const aspectRatios = ['1:1', '16:9', '9:16', '4:3', '3:4']
const editTypes = [
  { value: 'style_transfer', label: 'Style Transfer' },
  { value: 'pose_change', label: 'Pose Change' },
  { value: 'color_adjustment', label: 'Color Adjustment' },
  { value: 'background_replacement', label: 'Background Replacement' },
]
const prototypeTypes = [
  { value: 'app_screen', label: 'App Screen' },
  { value: 'icon', label: 'Icon' },
  { value: 'logo', label: 'Logo' },
  { value: 'banner', label: 'Banner' },
]

export default function ImagesPage() {
  const [activeTab, setActiveTab] = useState<'generate' | 'edit' | 'prototype'>('generate')
  const [selectedProvider, setSelectedProvider] = useState<'gemini' | 'openai' | 'imagen'>('gemini')
  const [jobResult, setJobResult] = useState<any>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  // Generate form
  const generateForm = useForm<GenerateFormData>({
    resolver: zodResolver(generateSchema),
    defaultValues: {
      provider: 'gemini',
      model: 'gemini-2.5-flash-image',
      aspect_ratio: '16:9',
      number_of_images: 1,
    },
  })

  // Edit form
  const editForm = useForm<EditFormData>({
    resolver: zodResolver(editSchema),
    defaultValues: {
      provider: 'gemini',
      model: 'gemini-2.5-flash-image',
      edit_type: 'style_transfer',
    },
  })

  // Prototype form
  const prototypeForm = useForm<PrototypeFormData>({
    resolver: zodResolver(prototypeSchema),
    defaultValues: {
      provider: 'gemini',
      model: 'gemini-2.5-flash-image',
      prototype_type: 'app_screen',
    },
  })

  const generateMutation = useMutation({
    mutationFn: (data: GenerateFormData) => {
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

  const editMutation = useMutation({
    mutationFn: async (data: EditFormData) => {
      if (!uploadedFile) throw new Error('Please upload an image first')

      // Convert file to base64
      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(uploadedFile)
      })

      const payload = {
        provider: data.provider,
        model: data.model,
        prompt: data.prompt,
        source_image: base64,
        edit_type: data.edit_type,
      }

      return fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/images/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(payload),
      }).then(res => res.json())
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const prototypeMutation = useMutation({
    mutationFn: (data: PrototypeFormData) => {
      const payload = {
        provider: data.provider,
        model: data.model,
        prompt: data.prompt,
        prototype_type: data.prototype_type,
        platform: data.platform,
      }

      return fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/images/prototype`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(payload),
      }).then(res => res.json())
    },
    onSuccess: (data) => {
      setJobResult(data)
    },
  })

  const handleProviderChange = (provider: 'gemini' | 'openai' | 'imagen') => {
    setSelectedProvider(provider)
    generateForm.setValue('provider', provider)
    generateForm.setValue('model', providerModels[provider][0])
    editForm.setValue('provider', provider)
    editForm.setValue('model', providerModels[provider][0])
    prototypeForm.setValue('provider', provider)
    prototypeForm.setValue('model', providerModels[provider][0])
  }

  // Check for template data on mount
  useEffect(() => {
    const templateDataStr = sessionStorage.getItem('templateData')
    if (templateDataStr) {
      try {
        const templateData = JSON.parse(templateDataStr)

        // Only apply if this is an image template
        if (templateData.template_type === 'image' && templateData.config) {
          const config = templateData.config

          // Pre-fill the generate form with template config
          if (config.provider) {
            handleProviderChange(config.provider)
          }
          if (config.prompt) {
            generateForm.setValue('prompt', config.prompt)
          }
          if (config.style_preset) {
            generateForm.setValue('style_preset', config.style_preset)
          }
          if (config.design_tokens?.primary_color) {
            generateForm.setValue('primary_color', config.design_tokens.primary_color)
          }
          if (config.design_tokens?.secondary_color) {
            generateForm.setValue('secondary_color', config.design_tokens.secondary_color)
          }
          if (config.image_config?.aspect_ratio) {
            generateForm.setValue('aspect_ratio', config.image_config.aspect_ratio)
          }
          if (config.image_config?.number_of_images) {
            generateForm.setValue('number_of_images', config.image_config.number_of_images)
          }
          if (config.negative_prompt) {
            generateForm.setValue('negative_prompt', config.negative_prompt)
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
        <h1 className="text-3xl font-bold">Image Generation</h1>
        <p className="text-muted-foreground">
          Create, edit, and prototype images with AI
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="space-y-6">
        <TabsList>
          <TabsTrigger value="generate">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate
          </TabsTrigger>
          <TabsTrigger value="edit">
            <Wand2 className="w-4 h-4 mr-2" />
            Edit
          </TabsTrigger>
          <TabsTrigger value="prototype">
            <Layout className="w-4 h-4 mr-2" />
            Prototype
          </TabsTrigger>
        </TabsList>

        {/* Generate Tab */}
        <TabsContent value="generate">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Generate Image</CardTitle>
                  <CardDescription>Create images from text descriptions</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={generateForm.handleSubmit((data) => generateMutation.mutate(data))} className="space-y-6">
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
                        {...generateForm.register('model')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        {providerModels[selectedProvider].map((model) => (
                          <option key={model} value={model}>{model}</option>
                        ))}
                      </select>
                    </div>

                    {/* Prompt */}
                    <div className="space-y-2">
                      <Label htmlFor="prompt">Prompt</Label>
                      <Textarea
                        id="prompt"
                        placeholder="A modern tech startup office with blue and white brand colors..."
                        rows={4}
                        {...generateForm.register('prompt')}
                      />
                      {generateForm.formState.errors.prompt && (
                        <p className="text-sm text-red-500">{generateForm.formState.errors.prompt.message}</p>
                      )}
                    </div>

                    {/* Style Preset */}
                    <div className="space-y-2">
                      <Label htmlFor="style_preset">Style Preset</Label>
                      <select
                        id="style_preset"
                        {...generateForm.register('style_preset')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        <option value="">None</option>
                        {stylePresets.map((style) => (
                          <option key={style} value={style}>{style.charAt(0).toUpperCase() + style.slice(1)}</option>
                        ))}
                      </select>
                    </div>

                    {/* Design Tokens */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="primary_color">Primary Color</Label>
                        <Input id="primary_color" type="color" {...generateForm.register('primary_color')} className="h-10" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="secondary_color">Secondary Color</Label>
                        <Input id="secondary_color" type="color" {...generateForm.register('secondary_color')} className="h-10" />
                      </div>
                    </div>

                    {/* Image Config */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="aspect_ratio">Aspect Ratio</Label>
                        <select
                          id="aspect_ratio"
                          {...generateForm.register('aspect_ratio')}
                          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                        >
                          {aspectRatios.map((ratio) => (
                            <option key={ratio} value={ratio}>{ratio}</option>
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
                          {...generateForm.register('number_of_images', { valueAsNumber: true })}
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
                        {...generateForm.register('negative_prompt')}
                      />
                    </div>

                    <Button type="submit" className="w-full" disabled={generateMutation.isPending}>
                      {generateMutation.isPending ? (
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

                    {generateMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(generateMutation.error as any)?.response?.data?.detail || 'Failed to generate image.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Result Panel */}
            <ResultPanel jobResult={jobResult} />
          </div>
        </TabsContent>

        {/* Edit Tab */}
        <TabsContent value="edit">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Edit Image</CardTitle>
                  <CardDescription>Transform existing images with AI</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={editForm.handleSubmit((data) => editMutation.mutate(data))} className="space-y-6">
                    {/* File Upload */}
                    <div className="space-y-2">
                      <Label>Source Image</Label>
                      <FileUpload
                        accept="image/*"
                        onChange={setUploadedFile}
                        value={uploadedFile}
                        maxSize={10}
                      />
                    </div>

                    {/* Provider & Model */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="edit_model">Model</Label>
                        <select
                          id="edit_model"
                          {...editForm.register('model')}
                          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                        >
                          {providerModels[selectedProvider].map((model) => (
                            <option key={model} value={model}>{model}</option>
                          ))}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="edit_type">Edit Type</Label>
                        <select
                          id="edit_type"
                          {...editForm.register('edit_type')}
                          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                        >
                          {editTypes.map((type) => (
                            <option key={type.value} value={type.value}>{type.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Prompt */}
                    <div className="space-y-2">
                      <Label htmlFor="edit_prompt">Edit Instructions</Label>
                      <Textarea
                        id="edit_prompt"
                        placeholder="Describe the changes you want..."
                        rows={4}
                        {...editForm.register('prompt')}
                      />
                      {editForm.formState.errors.prompt && (
                        <p className="text-sm text-red-500">{editForm.formState.errors.prompt.message}</p>
                      )}
                    </div>

                    <Button type="submit" className="w-full" disabled={editMutation.isPending || !uploadedFile}>
                      {editMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Wand2 className="mr-2 h-4 w-4" />
                          Edit Image
                        </>
                      )}
                    </Button>

                    {editMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(editMutation.error as any)?.message || 'Failed to edit image.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </div>

            <ResultPanel jobResult={jobResult} />
          </div>
        </TabsContent>

        {/* Prototype Tab */}
        <TabsContent value="prototype">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Generate Prototype</CardTitle>
                  <CardDescription>Create app screens, icons, logos, and banners</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={prototypeForm.handleSubmit((data) => prototypeMutation.mutate(data))} className="space-y-6">
                    {/* Prototype Type */}
                    <div className="space-y-2">
                      <Label htmlFor="prototype_type">Prototype Type</Label>
                      <div className="grid grid-cols-2 gap-3">
                        {prototypeTypes.map((type) => {
                          const selected = prototypeForm.watch('prototype_type') === type.value
                          return (
                            <Button
                              key={type.value}
                              type="button"
                              variant={selected ? 'default' : 'outline'}
                              onClick={() => prototypeForm.setValue('prototype_type', type.value as any)}
                              className="h-auto py-4"
                            >
                              <Layout className="w-5 h-5 mr-2" />
                              {type.label}
                            </Button>
                          )
                        })}
                      </div>
                    </div>

                    {/* Model */}
                    <div className="space-y-2">
                      <Label htmlFor="proto_model">Model</Label>
                      <select
                        id="proto_model"
                        {...prototypeForm.register('model')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        {providerModels[selectedProvider].map((model) => (
                          <option key={model} value={model}>{model}</option>
                        ))}
                      </select>
                    </div>

                    {/* Prompt */}
                    <div className="space-y-2">
                      <Label htmlFor="proto_prompt">Description</Label>
                      <Textarea
                        id="proto_prompt"
                        placeholder="Describe your prototype in detail..."
                        rows={4}
                        {...prototypeForm.register('prompt')}
                      />
                      {prototypeForm.formState.errors.prompt && (
                        <p className="text-sm text-red-500">{prototypeForm.formState.errors.prompt.message}</p>
                      )}
                    </div>

                    {/* Platform (optional for app screens) */}
                    {prototypeForm.watch('prototype_type') === 'app_screen' && (
                      <div className="space-y-2">
                        <Label htmlFor="platform">Platform (Optional)</Label>
                        <select
                          id="platform"
                          {...prototypeForm.register('platform')}
                          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                        >
                          <option value="">Any</option>
                          <option value="ios">iOS</option>
                          <option value="android">Android</option>
                          <option value="web">Web</option>
                        </select>
                      </div>
                    )}

                    <Button type="submit" className="w-full" disabled={prototypeMutation.isPending}>
                      {prototypeMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Layout className="mr-2 h-4 w-4" />
                          Generate Prototype
                        </>
                      )}
                    </Button>

                    {prototypeMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(prototypeMutation.error as any)?.message || 'Failed to generate prototype.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            </div>

            <ResultPanel jobResult={jobResult} />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

function ResultPanel({ jobResult }: { jobResult: any }) {
  return (
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
                <span className="text-sm">${jobResult.cost?.toFixed(4) || '0.0000'}</span>
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
                onClick={() => window.open(`/dashboard/jobs`, '_blank')}
              >
                View in Jobs
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
  )
}
