'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Image, Video, Sparkles, Zap, Shield, BarChart } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated())

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const features = [
    {
      icon: Image,
      title: 'AI Image Generation',
      description: 'Create stunning images with Gemini, OpenAI, and Imagen',
    },
    {
      icon: Video,
      title: 'AI Video Generation',
      description: 'Generate professional videos with Veo and Sora',
    },
    {
      icon: Zap,
      title: 'Batch Processing',
      description: 'Process multiple jobs efficiently with batch operations',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Encrypted API keys and secure data handling',
    },
    {
      icon: BarChart,
      title: 'Analytics Dashboard',
      description: 'Track usage, costs, and performance metrics',
    },
    {
      icon: Sparkles,
      title: 'Template Management',
      description: 'Save and reuse your best configurations',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <nav className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-xl">G</span>
            </div>
            <span className="font-bold text-xl">GTM Asset Generator</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </nav>

        <div className="text-center max-w-4xl mx-auto mb-20">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            Generate Marketing Assets with AI
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Create stunning images and videos for your marketing campaigns with
            Gemini, OpenAI, Imagen, Veo, and Sora. All in one platform.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Link href="/register">
              <Button size="lg" className="text-lg px-8">
                <Sparkles className="mr-2" />
                Start Creating
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-lg px-8">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow"
            >
              <feature.icon className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Marketing?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of businesses using AI to create amazing content
          </p>
          <Link href="/register">
            <Button size="lg" variant="secondary" className="text-lg px-8">
              Get Started Free
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
