'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatDistanceToNow } from 'date-fns'
import { RefreshCw, ExternalLink } from 'lucide-react'

export default function JobsPage() {
  const [currentPage, setCurrentPage] = useState(1)
  const [activeTab, setActiveTab] = useState<'images' | 'videos'>('images')

  const { data: imageJobs, isLoading: imageLoading, refetch: refetchImages } = useQuery({
    queryKey: ['image-jobs', currentPage],
    queryFn: () => apiClient.listImageJobs(currentPage, 20),
    enabled: activeTab === 'images',
  })

  const { data: videoJobs, isLoading: videoLoading, refetch: refetchVideos } = useQuery({
    queryKey: ['video-jobs', currentPage],
    queryFn: () => apiClient.listVideoJobs(currentPage, 20),
    enabled: activeTab === 'videos',
  })

  const jobs = activeTab === 'images' ? imageJobs : videoJobs
  const isLoading = activeTab === 'images' ? imageLoading : videoLoading
  const refetch = activeTab === 'images' ? refetchImages : refetchVideos

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Jobs</h1>
          <p className="text-muted-foreground">
            Track and monitor all your generation jobs
          </p>
        </div>
        <Button onClick={() => refetch()} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
        <TabsList>
          <TabsTrigger value="images">Images</TabsTrigger>
          <TabsTrigger value="videos">Videos</TabsTrigger>
        </TabsList>

        <TabsContent value="images" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Image Generation Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isLoading ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    Loading jobs...
                  </p>
                ) : jobs?.items && jobs.items.length > 0 ? (
                  <div className="space-y-3">
                    {jobs.items.map((job: any) => (
                      <div
                        key={job.id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                      >
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center space-x-2">
                            <p className="font-medium">{job.prompt || 'No prompt'}</p>
                            <Badge variant="outline" className="text-xs">
                              {job.provider}
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
                            <span>Model: {job.model}</span>
                            <span>Cost: ${job.cost.toFixed(4)}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Badge
                            variant={
                              job.status === 'completed'
                                ? 'success'
                                : job.status === 'failed'
                                ? 'destructive'
                                : 'secondary'
                            }
                          >
                            {job.status}
                          </Badge>
                          {job.result_url && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(job.result_url, '_blank')}
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No image jobs found
                  </p>
                )}

                {jobs && jobs.pages > 1 && (
                  <div className="flex justify-center space-x-2 pt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <span className="flex items-center px-4 text-sm">
                      Page {currentPage} of {jobs.pages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(jobs.pages, p + 1))}
                      disabled={currentPage === jobs.pages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="videos" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Video Generation Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isLoading ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    Loading jobs...
                  </p>
                ) : jobs?.items && jobs.items.length > 0 ? (
                  <div className="space-y-3">
                    {jobs.items.map((job: any) => (
                      <div
                        key={job.id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                      >
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center space-x-2">
                            <p className="font-medium">{job.prompt || 'No prompt'}</p>
                            <Badge variant="outline" className="text-xs">
                              {job.provider}
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
                            <span>Model: {job.model}</span>
                            <span>Cost: ${job.cost.toFixed(2)}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Badge
                            variant={
                              job.status === 'completed'
                                ? 'success'
                                : job.status === 'failed'
                                ? 'destructive'
                                : 'secondary'
                            }
                          >
                            {job.status}
                          </Badge>
                          {job.result_url && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(job.result_url, '_blank')}
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No video jobs found
                  </p>
                )}

                {jobs && jobs.pages > 1 && (
                  <div className="flex justify-center space-x-2 pt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <span className="flex items-center px-4 text-sm">
                      Page {currentPage} of {jobs.pages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(jobs.pages, p + 1))}
                      disabled={currentPage === jobs.pages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
