'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Plus, Trash2, FileText, Users as UsersIcon, Play, Edit } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const templateSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  description: z.string().optional(),
  template_type: z.enum(['image', 'video']),
  is_public: z.boolean().optional(),
})

type TemplateFormData = z.infer<typeof templateSchema>

export default function TemplatesPage() {
  const queryClient = useQueryClient()
  const router = useRouter()
  const [showCreate, setShowCreate] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [editingTemplate, setEditingTemplate] = useState<any>(null)

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates', currentPage],
    queryFn: () => apiClient.listTemplates(currentPage, 20),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TemplateFormData>({
    resolver: zodResolver(templateSchema),
    defaultValues: {
      template_type: 'image',
      is_public: false,
    },
  })

  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    setValue: setEditValue,
    formState: { errors: editErrors },
  } = useForm<TemplateFormData>({
    resolver: zodResolver(templateSchema),
  })

  const createMutation = useMutation({
    mutationFn: (data: TemplateFormData) =>
      apiClient.createTemplate({
        ...data,
        config: {}, // Empty config for now, can be filled from a form
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setShowCreate(false)
      reset()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: TemplateFormData }) =>
      apiClient.updateTemplate(id, {
        ...data,
        config: editingTemplate?.config || {},
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setEditingTemplate(null)
      resetEdit()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (templateId: string) => apiClient.deleteTemplate(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })

  const onSubmit = (data: TemplateFormData) => {
    createMutation.mutate(data)
  }

  const onSubmitEdit = (data: TemplateFormData) => {
    if (editingTemplate) {
      updateMutation.mutate({ id: editingTemplate.id, data })
    }
  }

  const handleEditTemplate = (template: any) => {
    setEditingTemplate(template)
    setEditValue('name', template.name)
    setEditValue('description', template.description || '')
    setEditValue('template_type', template.template_type)
    setEditValue('is_public', template.is_public)
  }

  const handleUseTemplate = (template: any) => {
    // Store template data in sessionStorage to be used by the generation page
    sessionStorage.setItem('templateData', JSON.stringify(template))

    // Navigate to the appropriate generation page
    if (template.template_type === 'image') {
      router.push('/dashboard/images')
    } else if (template.template_type === 'video') {
      router.push('/dashboard/videos')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground">
            Save and reuse your generation configurations
          </p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="w-4 h-4 mr-2" />
          New Template
        </Button>
      </div>

      {/* Create Template Form */}
      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>Create Template</CardTitle>
            <CardDescription>
              Save a configuration template for future use
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Template Name</Label>
                <Input
                  id="name"
                  placeholder="My Amazing Template"
                  {...register('name')}
                />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this template is for..."
                  rows={3}
                  {...register('description')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="template_type">Type</Label>
                <select
                  id="template_type"
                  {...register('template_type')}
                  className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="image">Image</option>
                  <option value="video">Video</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_public"
                  {...register('is_public')}
                  className="rounded"
                />
                <Label htmlFor="is_public">Make this template public</Label>
              </div>

              <div className="flex space-x-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Template'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreate(false)
                    reset()
                  }}
                >
                  Cancel
                </Button>
              </div>

              {createMutation.isError && (
                <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                  {(createMutation.error as any)?.response?.data?.detail ||
                    'Failed to create template. Please try again.'}
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      {/* Templates List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Templates</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              Loading templates...
            </p>
          ) : templates?.items && templates.items.length > 0 ? (
            <div className="space-y-3">
              {templates.items.map((template) => (
                <div
                  key={template.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <FileText className="w-5 h-5 text-muted-foreground" />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="font-medium">{template.name}</p>
                        <Badge variant="outline" className="text-xs">
                          {template.template_type}
                        </Badge>
                        {template.is_public && (
                          <Badge variant="secondary" className="text-xs">
                            Public
                          </Badge>
                        )}
                      </div>
                      {template.description && (
                        <p className="text-sm text-muted-foreground">
                          {template.description}
                        </p>
                      )}
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-1">
                        <span>
                          Created{' '}
                          {formatDistanceToNow(new Date(template.created_at), {
                            addSuffix: true,
                          })}
                        </span>
                        <span className="flex items-center">
                          <UsersIcon className="w-3 h-3 mr-1" />
                          {template.usage_count} uses
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleUseTemplate(template)}
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Use
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditTemplate(template)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMutation.mutate(template.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                No templates found. Create one to get started.
              </p>
              <Button onClick={() => setShowCreate(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Template
              </Button>
            </div>
          )}

          {templates && templates.pages > 1 && (
            <div className="flex justify-center space-x-2 pt-4 mt-4 border-t">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span className="flex items-center px-4 text-sm">
                Page {currentPage} of {templates.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(templates.pages, p + 1))}
                disabled={currentPage === templates.pages}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Template Dialog */}
      <Dialog open={!!editingTemplate} onOpenChange={(open) => !open && setEditingTemplate(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
            <DialogDescription>
              Update your template configuration
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmitEdit(onSubmitEdit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Template Name</Label>
              <Input
                id="edit-name"
                placeholder="My Amazing Template"
                {...registerEdit('name')}
              />
              {editErrors.name && (
                <p className="text-sm text-red-500">{editErrors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-description">Description (Optional)</Label>
              <Textarea
                id="edit-description"
                placeholder="Describe what this template is for..."
                rows={3}
                {...registerEdit('description')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-template_type">Type</Label>
              <select
                id="edit-template_type"
                {...registerEdit('template_type')}
                className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              >
                <option value="image">Image</option>
                <option value="video">Video</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit-is_public"
                {...registerEdit('is_public')}
                className="rounded"
              />
              <Label htmlFor="edit-is_public">Make this template public</Label>
            </div>

            <div className="flex space-x-2">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Updating...' : 'Update Template'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setEditingTemplate(null)
                  resetEdit()
                }}
              >
                Cancel
              </Button>
            </div>

            {updateMutation.isError && (
              <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                {(updateMutation.error as any)?.response?.data?.detail ||
                  'Failed to update template. Please try again.'}
              </div>
            )}
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
