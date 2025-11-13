'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Plus, Trash2, Key, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const apiKeySchema = z.object({
  provider: z.enum(['gemini', 'openai', 'google_cloud']),
  api_key: z.string().min(10, 'API key is required'),
})

type ApiKeyFormData = z.infer<typeof apiKeySchema>

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user)
  const queryClient = useQueryClient()
  const [showAddKey, setShowAddKey] = useState(false)

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiClient.getApiKeys(),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ApiKeyFormData>({
    resolver: zodResolver(apiKeySchema),
  })

  const createMutation = useMutation({
    mutationFn: (data: ApiKeyFormData) => apiClient.createApiKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setShowAddKey(false)
      reset()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.deleteApiKey(keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const onSubmit = (data: ApiKeyFormData) => {
    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and API keys
        </p>
      </div>

      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Email</Label>
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{user?.email}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Company</Label>
                  <span className="text-sm">{user?.company_name}</span>
                </div>
                <div className="space-y-2">
                  <Label>Account Status</Label>
                  <Badge variant={user?.is_active ? 'success' : 'destructive'}>
                    {user?.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <Label>Plan Tier</Label>
                  <Badge variant="outline">
                    {user?.tier || 'Free'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api-keys" className="mt-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium">API Keys</h3>
              <p className="text-sm text-muted-foreground">
                Manage your provider API keys for image and video generation
              </p>
            </div>
            <Button onClick={() => setShowAddKey(!showAddKey)} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add Key
            </Button>
          </div>

          {/* Add API Key Form */}
          {showAddKey && (
            <Card>
              <CardHeader>
                <CardTitle>Add API Key</CardTitle>
                <CardDescription>
                  Add a new provider API key to enable generation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="provider">Provider</Label>
                    <select
                      id="provider"
                      {...register('provider')}
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    >
                      <option value="gemini">Gemini</option>
                      <option value="openai">OpenAI</option>
                      <option value="google_cloud">Google Cloud</option>
                    </select>
                    {errors.provider && (
                      <p className="text-sm text-red-500">{errors.provider.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="api_key">API Key</Label>
                    <Input
                      id="api_key"
                      type="password"
                      placeholder="sk-..."
                      {...register('api_key')}
                    />
                    {errors.api_key && (
                      <p className="text-sm text-red-500">{errors.api_key.message}</p>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <Button type="submit" disabled={createMutation.isPending}>
                      {createMutation.isPending ? 'Adding...' : 'Add Key'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowAddKey(false)
                        reset()
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                  {createMutation.isError && (
                    <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                      {(createMutation.error as any)?.response?.data?.detail ||
                        'Failed to add API key. Please try again.'}
                    </div>
                  )}
                </form>
              </CardContent>
            </Card>
          )}

          {/* API Keys List */}
          <Card>
            <CardHeader>
              <CardTitle>Your API Keys</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  Loading API keys...
                </p>
              ) : apiKeys && apiKeys.length > 0 ? (
                <div className="space-y-3">
                  {apiKeys.map((key) => (
                    <div
                      key={key.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <Key className="w-5 h-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium capitalize">{key.provider}</p>
                          <p className="text-xs text-muted-foreground">
                            Added {formatDistanceToNow(new Date(key.created_at), { addSuffix: true })}
                            {key.last_used && (
                              <> • Last used {formatDistanceToNow(new Date(key.last_used), { addSuffix: true })}</>
                            )}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteMutation.mutate(key.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Key className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-sm text-muted-foreground">
                    No API keys found. Add one to start generating.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
