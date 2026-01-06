import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
    Database, Loader2, ArrowLeft, Sparkles, Calendar, Tag, RefreshCw
} from 'lucide-react'

const API_URL = "http://localhost:8000"

const cardVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.95 },
    visible: {
        y: 0,
        opacity: 1,
        scale: 1,
        transition: { type: "spring", stiffness: 100, damping: 15 }
    }
}

function ProgressPage() {
    const [progress, setProgress] = useState(null)
    const [history, setHistory] = useState([])
    const [isConnected, setIsConnected] = useState(false)

    useEffect(() => {
        const fetchProgress = async () => {
            try {
                const data = await fetch(`${API_URL}/progress`).then(res => res.json())
                setProgress(data)
                setIsConnected(true)

                // Add to history for trend tracking (keep last 20)
                setHistory(prev => {
                    const newHistory = [...prev, { ...data, timestamp: Date.now() }]
                    return newHistory.slice(-20)
                })
            } catch (e) {
                console.error('Progress fetch failed:', e)
                setIsConnected(false)
            }
        }

        fetchProgress()
        const interval = setInterval(fetchProgress, 2000) // 2s refresh for progress page
        return () => clearInterval(interval)
    }, [])

    // Calculate scraping rate of change
    const getRate = () => {
        if (history.length < 2) return null
        const recent = history.slice(-5)
        if (recent.length < 2) return null
        const first = recent[0]
        const last = recent[recent.length - 1]
        const timeDiff = (last.timestamp - first.timestamp) / 1000 // seconds
        const eventDiff = last.total_events - first.total_events
        return timeDiff > 0 ? (eventDiff / timeDiff * 60).toFixed(1) : 0 // per minute
    }

    // Calculate AI enrichment rate
    const getAiRate = () => {
        if (history.length < 2) return null
        const recent = history.slice(-5)
        if (recent.length < 2) return null
        const first = recent[0]
        const last = recent[recent.length - 1]
        const timeDiff = (last.timestamp - first.timestamp) / 1000 // seconds
        const summaryDiff = last.total_summaries - first.total_summaries
        return timeDiff > 0 ? (summaryDiff / timeDiff * 60).toFixed(1) : 0 // per minute
    }

    const aiRate = getAiRate()

    // Calculate ETA for AI enrichment
    const getEta = () => {
        const rate = parseFloat(aiRate)
        if (!rate || rate <= 0 || !progress?.remaining) return null
        const minutesRemaining = progress.remaining / rate
        if (minutesRemaining < 60) {
            return `~${Math.ceil(minutesRemaining)} min`
        } else {
            const hours = Math.floor(minutesRemaining / 60)
            const mins = Math.round(minutesRemaining % 60)
            return `~${hours}h ${mins}m`
        }
    }

    const rate = getRate()
    const eta = getEta()

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 font-sans text-white">
            {/* Animated Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        x: [0, 100, 0],
                        y: [0, -50, 0],
                    }}
                    transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute top-0 right-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
                />
                <motion.div
                    animate={{
                        scale: [1, 1.3, 1],
                        x: [0, -80, 0],
                        y: [0, 100, 0],
                    }}
                    transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"
                />
            </div>

            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-20"
            >
                <div className="max-w-[1200px] mx-auto px-8 py-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link
                            to="/"
                            className="p-2 bg-white/10 rounded-xl hover:bg-white/20 transition-colors"
                        >
                            <ArrowLeft size={20} />
                        </Link>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-200 via-pink-200 to-purple-200 bg-clip-text text-transparent">
                                Live Scraping Progress
                            </h1>
                            <p className="text-purple-300 text-sm mt-0.5">Real-time monitoring • Auto-refresh: 2s</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${isConnected ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                            }`}>
                            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                            {isConnected ? 'Connected' : 'Disconnected'}
                        </div>
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                            <RefreshCw size={20} className="text-purple-400" />
                        </motion.div>
                    </div>
                </div>
            </motion.header>

            {/* Main Content */}
            <main className="relative z-10 p-8 max-w-[1200px] mx-auto">
                {progress ? (
                    <div className="space-y-8">
                        {/* Big Stats Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {/* Total Events - Large */}
                            <motion.div
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                className="lg:col-span-2 bg-gradient-to-br from-purple-500 to-pink-500 p-[1px] rounded-2xl"
                            >
                                <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-8 h-full">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-purple-300 text-sm font-medium mb-2">Events Scraped</p>
                                            <motion.p
                                                key={progress.total_events}
                                                initial={{ scale: 1.2, color: '#f0abfc' }}
                                                animate={{ scale: 1, color: '#ffffff' }}
                                                className="text-6xl font-bold"
                                            >
                                                {progress.total_events?.toLocaleString() || 0}
                                            </motion.p>
                                            {rate !== null && (
                                                <p className="text-green-400 text-sm mt-2">
                                                    +{rate} events/min
                                                </p>
                                            )}
                                        </div>
                                        <div className="p-6 bg-white/10 rounded-2xl">
                                            <Database size={48} className="text-purple-400" />
                                        </div>
                                    </div>
                                </div>
                            </motion.div>

                            {/* AI Summaries */}
                            <motion.div
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                transition={{ delay: 0.1 }}
                                className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
                            >
                                <div className="flex flex-col items-center">
                                    <div className="relative w-28 h-28 mb-4">
                                        <svg className="w-full h-full transform -rotate-90">
                                            <circle cx="56" cy="56" r="48" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10" />
                                            <motion.circle
                                                cx="56" cy="56" r="48" fill="none" stroke="url(#summaryGrad)" strokeWidth="10"
                                                strokeLinecap="round"
                                                strokeDasharray={301.6}
                                                animate={{ strokeDashoffset: 301.6 * (1 - (progress.summary_percentage || 0) / 100) }}
                                                transition={{ duration: 0.5 }}
                                            />
                                            <defs>
                                                <linearGradient id="summaryGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                                    <stop offset="0%" stopColor="#f093fb" />
                                                    <stop offset="100%" stopColor="#f5576c" />
                                                </linearGradient>
                                            </defs>
                                        </svg>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <Sparkles size={28} className="text-pink-400" />
                                        </div>
                                    </div>
                                    <p className="text-3xl font-bold text-white">{progress.summary_percentage || 0}%</p>
                                    <p className="text-purple-300 text-sm">{progress.total_summaries?.toLocaleString() || 0} AI Summaries</p>
                                    {aiRate > 0 && (
                                        <p className="text-pink-400 text-xs mt-1">+{aiRate}/min {eta && `• ETA: ${eta}`}</p>
                                    )}
                                </div>
                            </motion.div>

                            {/* Events with Dates */}
                            <motion.div
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                transition={{ delay: 0.2 }}
                                className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
                            >
                                <div className="flex flex-col items-center">
                                    <div className="relative w-28 h-28 mb-4">
                                        <svg className="w-full h-full transform -rotate-90">
                                            <circle cx="56" cy="56" r="48" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10" />
                                            <motion.circle
                                                cx="56" cy="56" r="48" fill="none" stroke="url(#dateGrad)" strokeWidth="10"
                                                strokeLinecap="round"
                                                strokeDasharray={301.6}
                                                animate={{ strokeDashoffset: 301.6 * (1 - (progress.date_percentage || 0) / 100) }}
                                                transition={{ duration: 0.5 }}
                                            />
                                            <defs>
                                                <linearGradient id="dateGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                                    <stop offset="0%" stopColor="#00f2fe" />
                                                    <stop offset="100%" stopColor="#4facfe" />
                                                </linearGradient>
                                            </defs>
                                        </svg>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <Calendar size={28} className="text-cyan-400" />
                                        </div>
                                    </div>
                                    <p className="text-3xl font-bold text-white">{progress.date_percentage || 0}%</p>
                                    <p className="text-purple-300 text-sm">{progress.events_with_dates?.toLocaleString() || 0} With Dates</p>
                                </div>
                            </motion.div>
                        </div>

                        {/* Second Row */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Categorized */}
                            <motion.div
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                transition={{ delay: 0.3 }}
                                className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="relative w-20 h-20">
                                        <svg className="w-full h-full transform -rotate-90">
                                            <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
                                            <motion.circle
                                                cx="40" cy="40" r="32" fill="none" stroke="url(#catGrad)" strokeWidth="8"
                                                strokeLinecap="round"
                                                strokeDasharray={201}
                                                animate={{ strokeDashoffset: 201 * (1 - (progress.category_percentage || 0) / 100) }}
                                                transition={{ duration: 0.5 }}
                                            />
                                            <defs>
                                                <linearGradient id="catGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                                    <stop offset="0%" stopColor="#43e97b" />
                                                    <stop offset="100%" stopColor="#38f9d7" />
                                                </linearGradient>
                                            </defs>
                                        </svg>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <Tag size={20} className="text-green-400" />
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-2xl font-bold text-white">{progress.category_percentage || 0}%</p>
                                        <p className="text-purple-300 text-sm">{progress.events_with_categories?.toLocaleString() || 0} Categorized</p>
                                        <p className="text-purple-400 text-xs">Non-generic categories</p>
                                    </div>
                                </div>
                            </motion.div>

                            {/* Recent AI Activity */}
                            <motion.div
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                transition={{ delay: 0.4 }}
                                className="md:col-span-2 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
                            >
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Sparkles size={18} className="text-pink-400" />
                                    Recent AI Activity
                                </h3>
                                {progress.latest_summaries && progress.latest_summaries.length > 0 ? (
                                    <div className="space-y-3">
                                        {progress.latest_summaries.map((item, i) => (
                                            <motion.div
                                                key={i}
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: i * 0.1 }}
                                                className="flex items-center justify-between bg-white/5 rounded-lg p-3"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center text-xs font-bold">
                                                        {item.quality_score || '?'}
                                                    </div>
                                                    <div>
                                                        <p className="text-white text-sm font-medium">{item.title}</p>
                                                        <p className="text-purple-400 text-xs">{item.category}</p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-6">
                                        <p className="text-purple-400 text-sm">No AI summaries yet</p>
                                        <p className="text-purple-500 text-xs mt-1">Run <code className="bg-white/10 px-1.5 py-0.5 rounded">make ai-enrich</code></p>
                                    </div>
                                )}
                            </motion.div>
                        </div>

                        {/* Third Row - Pipeline Status */}
                        <motion.div
                            variants={cardVariants}
                            initial="hidden"
                            animate="visible"
                            transition={{ delay: 0.5 }}
                            className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Pipeline Status</h3>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                                    <span className="text-purple-300">Scraping</span>
                                    <span className="text-green-400 flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                                        Active
                                    </span>
                                </div>
                                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                                    <span className="text-purple-300">AI Enrichment</span>
                                    <span className={`flex items-center gap-2 ${progress.total_summaries > 0 && aiRate > 0 ? 'text-green-400' : 'text-yellow-400'}`}>
                                        <div className={`w-2 h-2 rounded-full ${progress.total_summaries > 0 && aiRate > 0 ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`} />
                                        {progress.total_summaries > 0 && aiRate > 0 ? 'Active' : 'Pending'}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                                    <span className="text-purple-300">Database</span>
                                    <span className="text-green-400 flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-green-400" />
                                        Connected
                                    </span>
                                </div>
                                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                                    <span className="text-purple-300">Remaining</span>
                                    <span className="text-white font-mono font-bold">
                                        {progress.remaining?.toLocaleString() || 0}
                                    </span>
                                </div>
                            </div>
                        </motion.div>

                        {/* Tips */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                            className="text-center text-purple-400 text-sm"
                        >
                            💡 Run <code className="bg-white/10 px-2 py-1 rounded">make scrape</code> in terminal to start scraping •
                            Run <code className="bg-white/10 px-2 py-1 rounded">make ai-enrich</code> to generate AI summaries
                        </motion.div>
                    </div>
                ) : (
                    <div className="flex items-center justify-center h-64">
                        <div className="text-center">
                            <Loader2 size={48} className="text-purple-400 animate-spin mx-auto mb-4" />
                            <p className="text-purple-300">Connecting to backend...</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}

export default ProgressPage
