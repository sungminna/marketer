'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Layers, CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function BatchesPage() {
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null)

  const { data: batches, isLoading: batchesLoading } = useQuery({
    queryKey: ['batches', currentPage],
    queryFn: () => apiClient.listBatches(currentPage, 20),
  })

  const { data: batchJobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['batch-jobs', selectedBatch],
    queryFn: () => apiClient.getBatchJobs(selectedBatch!, 1, 20),
    enabled: !!selectedBatch,
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'destructive'
      case 'processing':
        return 'warning'
      default:
        return 'secondary'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Batch Processing</h1>
          <p className="text-muted-foreground">
            Manage and monitor your batch generation jobs
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Batches List */}
        <Card>
          <CardHeader>
            <CardTitle>Batches</CardTitle>
            <CardDescription>Your batch processing jobs</CardDescription>
          </CardHeader>
          <CardContent>
            {batchesLoading ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                Loading batches...
              </p>
            ) : batches?.items && batches.items.length > 0 ? (
              <div className="space-y-3">
                {batches.items.map((batch) => (
                  <div
                    key={batch.id}
                    className={`flex flex-col p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedBatch === batch.id
                        ? 'bg-accent'
                        : 'hover:bg-accent'
                    }`}
                    onClick={() => setSelectedBatch(batch.id)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Layers className="w-5 h-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{batch.name}</p>
                          {batch.description && (
                            <p className="text-sm text-muted-foreground">
                              {batch.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge variant={getStatusColor(batch.status) as any}>
                        {batch.status}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Total Jobs</p>
                        <p className="font-medium">{batch.total_jobs}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Completed</p>
                        <p className="font-medium text-green-600">
                          {batch.completed_jobs}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Failed</p>
                        <p className="font-medium text-red-600">
                          {batch.failed_jobs}
                        </p>
                      </div>
                    </div>

                    <div className="mt-3 pt-3 border-t">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>
                          Created {formatDistanceToNow(new Date(batch.created_at), { addSuffix: true })}
                        </span>
                        <span>
                          {Math.round((batch.completed_jobs / batch.total_jobs) * 100)}% complete
                        </span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-1.5 mt-2">
                        <div
                          className="bg-primary h-1.5 rounded-full transition-all"
                          style={{
                            width: `${(batch.completed_jobs / batch.total_jobs) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Layers className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-sm text-muted-foreground mb-4">
                  No batches found.
                </p>
                <p className="text-xs text-muted-foreground">
                  Create batches through the API to process multiple jobs at once.
                </p>
              </div>
            )}

            {batches && batches.pages > 1 && (
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
                  Page {currentPage} of {batches.pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.min(batches.pages, p + 1))}
                  disabled={currentPage === batches.pages}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Batch Jobs */}
        <Card>
          <CardHeader>
            <CardTitle>Batch Jobs</CardTitle>
            <CardDescription>
              {selectedBatch
                ? 'Jobs in this batch'
                : 'Select a batch to view its jobs'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedBatch ? (
              <p className="text-sm text-muted-foreground text-center py-12">
                Select a batch from the list to view its jobs
              </p>
            ) : jobsLoading ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                Loading jobs...
              </p>
            ) : batchJobs?.items && batchJobs.items.length > 0 ? (
              <div className="space-y-3">
                {batchJobs.items.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-start justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-start space-x-3 flex-1">
                      {getStatusIcon(job.status)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <p className="text-sm font-medium">
                            {job.prompt?.slice(0, 50) || job.job_type}
                            {job.prompt && job.prompt.length > 50 ? '...' : ''}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                          <Badge variant="outline" className="text-xs">
                            {job.provider}
                          </Badge>
                          <span>Cost: ${job.cost.toFixed(4)}</span>
                          <span>
                            {formatDistanceToNow(new Date(job.created_at), {
                              addSuffix: true,
                            })}
                          </span>
                        </div>
                        {job.error_message && (
                          <p className="text-xs text-red-500 mt-2">
                            {job.error_message}
                          </p>
                        )}
                      </div>
                    </div>
                    <Badge variant={getStatusColor(job.status) as any}>
                      {job.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-sm text-muted-foreground">
                  No jobs found in this batch.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>About Batch Processing</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            Batch processing allows you to submit multiple generation jobs at once
            and monitor their progress collectively.
          </p>
          <p>
            To create a batch, use the API endpoint:{' '}
            <code className="bg-secondary px-2 py-1 rounded">
              POST /api/v1/batches
            </code>
          </p>
          <p>
            Each batch can contain multiple image or video generation jobs with
            different configurations. Jobs in a batch are processed asynchronously.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
