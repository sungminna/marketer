'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Plus, Trash2, Webhook as WebhookIcon, CheckCircle, XCircle, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const webhookSchema = z.object({
  url: z.string().url('Must be a valid URL'),
  events: z.array(z.string()).min(1, 'Select at least one event'),
  secret: z.string().optional(),
})

type WebhookFormData = z.infer<typeof webhookSchema>

const availableEvents = [
  'job.created',
  'job.completed',
  'job.failed',
  'job.processing',
]

export default function WebhooksPage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [selectedWebhook, setSelectedWebhook] = useState<string | null>(null)
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['job.completed'])

  const { data: webhooks, isLoading } = useQuery({
    queryKey: ['webhooks'],
    queryFn: () => apiClient.listWebhooks(),
  })

  const { data: deliveries, isLoading: deliveriesLoading } = useQuery({
    queryKey: ['webhook-deliveries', selectedWebhook],
    queryFn: () => apiClient.getWebhookDeliveries(selectedWebhook!, 1, 20),
    enabled: !!selectedWebhook,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<WebhookFormData>({
    resolver: zodResolver(webhookSchema),
  })

  const createMutation = useMutation({
    mutationFn: (data: WebhookFormData) =>
      apiClient.createWebhook({
        ...data,
        events: selectedEvents,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      setShowCreate(false)
      setSelectedEvents(['job.completed'])
      reset()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (webhookId: string) => apiClient.deleteWebhook(webhookId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      setSelectedWebhook(null)
    },
  })

  const onSubmit = (data: Omit<WebhookFormData, 'events'>) => {
    createMutation.mutate({
      ...data,
      events: selectedEvents,
    })
  }

  const toggleEvent = (event: string) => {
    setSelectedEvents((prev) =>
      prev.includes(event)
        ? prev.filter((e) => e !== event)
        : [...prev, event]
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Webhooks</h1>
          <p className="text-muted-foreground">
            Receive real-time notifications for job events
          </p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Webhook
        </Button>
      </div>

      {/* Create Webhook Form */}
      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>Create Webhook</CardTitle>
            <CardDescription>
              Configure a webhook endpoint to receive job event notifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="url">Webhook URL</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://api.example.com/webhooks"
                  {...register('url')}
                />
                {errors.url && (
                  <p className="text-sm text-red-500">{errors.url.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Events to Subscribe</Label>
                <div className="space-y-2">
                  {availableEvents.map((event) => (
                    <div key={event} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={event}
                        checked={selectedEvents.includes(event)}
                        onChange={() => toggleEvent(event)}
                        className="rounded"
                      />
                      <Label htmlFor={event} className="font-normal">
                        {event}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="secret">Secret (Optional)</Label>
                <Input
                  id="secret"
                  type="password"
                  placeholder="Your webhook secret"
                  {...register('secret')}
                />
                <p className="text-xs text-muted-foreground">
                  Used to verify webhook authenticity
                </p>
              </div>

              <div className="flex space-x-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Webhook'}
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
                    'Failed to create webhook. Please try again.'}
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Webhooks List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Webhooks</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                Loading webhooks...
              </p>
            ) : webhooks && webhooks.length > 0 ? (
              <div className="space-y-3">
                {webhooks.map((webhook) => (
                  <div
                    key={webhook.id}
                    className={`flex items-start justify-between p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedWebhook === webhook.id
                        ? 'bg-accent'
                        : 'hover:bg-accent'
                    }`}
                    onClick={() => setSelectedWebhook(webhook.id)}
                  >
                    <div className="flex items-start space-x-3 flex-1">
                      <WebhookIcon className="w-5 h-5 text-muted-foreground mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="font-medium text-sm break-all">{webhook.url}</p>
                          <Badge variant={webhook.is_active ? 'success' : 'secondary'}>
                            {webhook.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {webhook.events.map((event) => (
                            <Badge key={event} variant="outline" className="text-xs">
                              {event}
                            </Badge>
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Created {formatDistanceToNow(new Date(webhook.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteMutation.mutate(webhook.id)
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <WebhookIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-sm text-muted-foreground mb-4">
                  No webhooks configured. Create one to get started.
                </p>
                <Button onClick={() => setShowCreate(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Webhook
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Delivery Log */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Deliveries</CardTitle>
            <CardDescription>
              {selectedWebhook
                ? 'Webhook delivery attempts and results'
                : 'Select a webhook to view deliveries'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedWebhook ? (
              <p className="text-sm text-muted-foreground text-center py-12">
                Select a webhook from the list to view delivery history
              </p>
            ) : deliveriesLoading ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                Loading deliveries...
              </p>
            ) : deliveries?.items && deliveries.items.length > 0 ? (
              <div className="space-y-3">
                {deliveries.items.map((delivery) => (
                  <div
                    key={delivery.id}
                    className="flex items-start justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-start space-x-3 flex-1">
                      {delivery.status === 'success' ? (
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="text-sm font-medium">{delivery.event}</p>
                          <Badge
                            variant={delivery.status === 'success' ? 'success' : 'destructive'}
                            className="text-xs"
                          >
                            {delivery.status}
                          </Badge>
                        </div>
                        {delivery.response_status && (
                          <p className="text-xs text-muted-foreground">
                            HTTP {delivery.response_status}
                          </p>
                        )}
                        {delivery.error_message && (
                          <p className="text-xs text-red-500 mt-1">
                            {delivery.error_message}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDistanceToNow(new Date(delivery.delivered_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-sm text-muted-foreground">
                  No deliveries yet. Webhook events will appear here.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
