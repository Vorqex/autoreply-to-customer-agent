'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { PageTransition } from '@/components/layout/page-transition'
import {
  Settings2,
  FileText,
  Play,
  History,
  RefreshCw,
  AlertCircle,
  Folder,
} from 'lucide-react'

const folderPath = 'C:\\Auto-reply Agent\\data\\agent'

const folderFiles = ['config.json', 'templates.json']

const agentConfig = {
  model: 'gpt-4',
  temperature: 0.7,
  max_tokens: 300,
  tone: 'professional',
  auto_reply_enabled: true,
  schedule_interval_minutes: 60,
}

const replyTemplates = [
  { name: 'Thank You', trigger: 'positive', variant: 'default' as const },
  { name: 'Apology', trigger: 'negative', variant: 'destructive' as const },
  { name: 'Neutral Response', trigger: 'neutral', variant: 'secondary' as const },
]

const stagger = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

export default function AgentPage() {
  const [agentEnabled] = useState(true)
  const [running, setRunning] = useState(false)

  const handleRunAgent = () => {
    setRunning(true)
    toast.success('Agent run started')
    setTimeout(() => {
      setRunning(false)
      toast.success('Agent run completed')
    }, 3000)
  }

  return (
    <PageTransition>
      <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-6">
        <motion.div variants={item} className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Auto-Reply Agent</h2>
            <p className="text-sm text-muted-foreground">
              Manage your AI agent configuration and monitor its activity
            </p>
          </div>
          <Badge
            variant="outline"
            className={cn(
              'gap-1.5 px-3 py-1.5 text-sm',
              agentEnabled
                ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-400'
                : 'border-neutral-200 bg-neutral-50 text-neutral-600 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400'
            )}
          >
            <span className={cn('h-2 w-2 rounded-full', agentEnabled ? 'bg-emerald-500' : 'bg-neutral-400')} />
            {agentEnabled ? 'Active' : 'Paused'}
          </Badge>
        </motion.div>

        <motion.div variants={item} className="grid gap-6 lg:grid-cols-3">
          <Card glass className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <Settings2 className="h-4 w-4" />
                  Configuration
                </CardTitle>
                <Button variant="outline" size="sm" onClick={() => toast.success('Config reloaded')}>
                  <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Model', value: agentConfig.model },
                    { label: 'Temperature', value: agentConfig.temperature },
                    { label: 'Max Tokens', value: agentConfig.max_tokens },
                    { label: 'Tone', value: agentConfig.tone },
                  ].map((field) => (
                    <div key={field.label} className="rounded-lg border bg-muted/30 px-4 py-3">
                      <p className="text-xs text-muted-foreground">{field.label}</p>
                      <p className="mt-0.5 text-sm font-medium text-foreground">{String(field.value)}</p>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between rounded-lg border bg-muted/30 px-4 py-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Auto-Reply</p>
                    <p className="mt-0.5 text-sm font-medium text-foreground">
                      {agentConfig.auto_reply_enabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <Badge variant={agentConfig.auto_reply_enabled ? 'default' : 'secondary'}>
                    Every {agentConfig.schedule_interval_minutes} min
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card glass>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Folder className="h-4 w-4" />
                Agent Folder
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="rounded-lg border bg-muted/30 px-4 py-3">
                  <p className="text-xs text-muted-foreground">Path</p>
                  <p className="mt-0.5 truncate text-sm font-medium text-foreground" title={folderPath}>
                    {folderPath}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-lg border bg-muted/30 px-4 py-3">
                    <p className="text-xs text-muted-foreground">Files</p>
                    <p className="mt-0.5 text-lg font-bold text-foreground">{folderFiles.length}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 px-4 py-3">
                    <p className="text-xs text-muted-foreground">Size</p>
                    <p className="mt-0.5 text-lg font-bold text-foreground">~1.2 KB</p>
                  </div>
                </div>
                {folderFiles.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs text-muted-foreground">Files</p>
                    <div className="space-y-1">
                      {folderFiles.map((file: string) => (
                        <div key={file} className="flex items-center gap-2 rounded-md bg-muted/20 px-3 py-1.5">
                          <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                          <span className="text-xs text-foreground">{file}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
          <Card glass>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Reply Templates
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {replyTemplates.map((template) => (
                <div
                  key={template.name}
                  className="flex items-center justify-between rounded-lg border bg-muted/20 p-3"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium text-foreground">{template.name}</p>
                      <p className="text-xs text-muted-foreground">Trigger: {template.trigger}</p>
                    </div>
                  </div>
                  <Badge variant={template.variant}>{template.trigger}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card glass>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <History className="h-4 w-4" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                className="w-full"
                onClick={handleRunAgent}
                disabled={running}
              >
                {running ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Agent Now
                  </>
                )}
              </Button>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="w-full" onClick={() => toast.info('Opening folder...')}>
                  <Folder className="mr-2 h-4 w-4" />
                  Open Folder
                </Button>
                <Button variant="outline" className="w-full" onClick={() => toast.success('Config reloaded')}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Reload Config
                </Button>
              </div>
              <Separator />
              <div className="rounded-lg border bg-amber-50/50 p-3 dark:bg-amber-950/20">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                  <p className="text-xs font-medium text-amber-700 dark:text-amber-400">Agent Status</p>
                </div>
                <p className="mt-1 text-xs text-amber-600/80 dark:text-amber-400/80">
                  {agentEnabled
                    ? 'The agent is active and will process reviews on schedule.'
                    : 'The agent is paused. Enable it to resume automatic replies.'}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </PageTransition>
  )
}
