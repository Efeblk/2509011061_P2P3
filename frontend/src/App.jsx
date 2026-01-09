import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area, Legend, ComposedChart,
  ScatterChart, Scatter, ZAxis
} from 'recharts'
import {
  TrendingUp, Users, Activity, PieChart as PieChartIcon,
  ArrowUpRight, ArrowDownRight, CheckCircle2, Database, Loader2, Calendar, Tag
} from 'lucide-react'

const API_URL = "http://localhost:8000"

// Gradient color palette
const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a']

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 }
  }
}

const cardVariants = {
  hidden: { y: 20, opacity: 0, scale: 0.95 },
  visible: {
    y: 0,
    opacity: 1,
    scale: 1,
    transition: { type: "spring", stiffness: 100, damping: 15 }
  }
}

function App() {
  const [analysis, setAnalysis] = useState(null)
  const [categories, setCategories] = useState([])
  const [dataQuality, setDataQuality] = useState(null)
  const [advancedAnalysis, setAdvancedAnalysis] = useState(null)
  const [featured, setFeatured] = useState(null)
  const [scatterData, setScatterData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [fullAnalysis, categoryData, advancedData, featuredData, scatterResult] = await Promise.all([
          fetch(`${API_URL}/analysis/full`).then(res => res.json()),
          fetch(`${API_URL}/analysis/categories`).then(res => res.json()),
          fetch(`${API_URL}/analysis/advanced`).then(res => res.json()),
          fetch(`${API_URL}/featured`).then(res => res.json()),
          fetch(`${API_URL}/scatter`).then(res => res.json())
        ])
        setAnalysis(fullAnalysis)
        setCategories(Array.isArray(categoryData) ? categoryData : [])
        setAdvancedAnalysis(advancedData)
        setFeatured(featuredData)
        setScatterData(Array.isArray(scatterResult) ? scatterResult : [])

        // Set data quality score from anomaly detection results
        if (fullAnalysis && fullAnalysis.anomalies) {
          const qualityScore = Math.round(100 - fullAnalysis.anomalies.rate)
          setDataQuality(qualityScore)
        }

        setLoading(false)
      } catch (e) {
        console.error(e)
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-white text-lg font-medium">Loading Dashboard...</p>
        </motion.div>
      </div>
    )
  }

  // Filter and prepare data
  if (!analysis || !analysis.summary) {
    return (
      <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-lg font-medium mb-2">Failed to load data</p>
          <p className="text-purple-300 text-sm">Please check if the backend is running</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const topCategories = categories.filter(c => c.name !== 'Etkinlik' && c.name).slice(0, 10)
  const pieData = topCategories.slice(0, 6)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 font-sans text-white overflow-x-hidden">

      {/* Animated Background Orbs */}
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

      {/* Main Content */}
      <main className="relative z-10">
        {/* Top Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-20"
        >
          <div className="max-w-[1600px] mx-auto px-8 py-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
                className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/50"
              >
                <Activity size={24} className="text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-200 via-pink-200 to-purple-200 bg-clip-text text-transparent">
                  EventGraph Dashboard
                </h1>
                <p className="text-purple-300 text-sm mt-0.5">Real-time Istanbul event analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                to="/progress"
                className="bg-white/10 hover:bg-white/20 text-white font-semibold px-5 py-2.5 rounded-xl transition-all flex items-center gap-2"
              >
                <Database size={18} />
                Live Progress
              </Link>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.reload()}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-2.5 rounded-xl transition-all shadow-lg shadow-purple-500/50"
              >
                Refresh Data
              </motion.button>
            </div>
          </div>
        </motion.header>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="p-8 max-w-[1600px] mx-auto space-y-8"
        >

          {/* KPI Cards */}
          <motion.div
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <KpiCard
              title="Total Events"
              value={analysis.summary.total_events.toLocaleString()}
              trend={`${analysis.anomalies.rate}% anomalies`}
              trendUp={false}
              icon={<Database />}
              gradient="from-blue-500 to-cyan-500"
            />
            <KpiCard
              title="Mean Price"
              value={`${analysis.summary.mean_price.toFixed(0)} TL`}
              trend={`σ=${analysis.summary.std_dev.toFixed(0)}`}
              trendUp
              icon={<TrendingUp />}
              gradient="from-purple-500 to-pink-500"
            />
            <KpiCard
              title="Median Price"
              value={`${analysis.summary.median_price.toFixed(0)} TL`}
              trend={`IQR=${analysis.distribution.iqr.toFixed(0)}`}
              trendUp
              icon={<Activity />}
              gradient="from-green-500 to-emerald-500"
            />
            <KpiCard
              title="Categories"
              value={analysis.summary.total_categories}
              trend={`${analysis.summary.total_venues} venues`}
              trendUp
              icon={<Users />}
              gradient="from-orange-500 to-red-500"
            />
          </motion.div>

          {/* Featured Events Section */}
          {featured && (
            <motion.div
              variants={cardVariants}
              className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
            >
              <div className="px-6 py-5 border-b border-white/10 bg-gradient-to-r from-emerald-500/10 to-teal-500/10">
                <h3 className="font-semibold text-xl text-white flex items-center gap-2">
                  🎪 Featured Events
                </h3>
                <p className="text-purple-300 text-sm mt-1">
                  AI-enriched events across price ranges
                </p>
              </div>
              <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Cheapest Events */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-green-400 flex items-center gap-2">
                    💚 Budget-Friendly
                    <span className="text-xs text-purple-400 font-normal">Lowest prices</span>
                  </h4>
                  {featured.cheapest?.map((event, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-xl p-4 border border-green-500/20"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="text-white font-medium text-sm leading-tight">{event.title}</h5>
                        <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded-full font-bold">
                          {event.price} TL
                        </span>
                      </div>
                      <p className="text-purple-300 text-xs mb-2">{event.venue} • {event.category}</p>
                      {event.summary && (
                        <p className="text-purple-400 text-xs italic">"{event.summary}"</p>
                      )}
                      <div className="flex items-center gap-1 mt-2">
                        <span className="text-yellow-400 text-xs">AI Score:</span>
                        <span className="text-white text-xs font-bold">{event.quality_score}/10</span>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Medium Events */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-blue-400 flex items-center gap-2">
                    💙 Mid-Range
                    <span className="text-xs text-purple-400 font-normal">Best value</span>
                  </h4>
                  {featured.medium?.map((event, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 + 0.3 }}
                      className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-xl p-4 border border-blue-500/20"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="text-white font-medium text-sm leading-tight">{event.title}</h5>
                        <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full font-bold">
                          {event.price} TL
                        </span>
                      </div>
                      <p className="text-purple-300 text-xs mb-2">{event.venue} • {event.category}</p>
                      {event.summary && (
                        <p className="text-purple-400 text-xs italic">"{event.summary}"</p>
                      )}
                      <div className="flex items-center gap-1 mt-2">
                        <span className="text-yellow-400 text-xs">AI Score:</span>
                        <span className="text-white text-xs font-bold">{event.quality_score}/10</span>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Premium Events */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-pink-400 flex items-center gap-2">
                    💎 Premium
                    <span className="text-xs text-purple-400 font-normal">Luxury experiences</span>
                  </h4>
                  {featured.premium?.map((event, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 + 0.6 }}
                      className="bg-gradient-to-br from-pink-500/10 to-purple-500/10 rounded-xl p-4 border border-pink-500/20"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="text-white font-medium text-sm leading-tight">{event.title}</h5>
                        <span className="bg-pink-500/20 text-pink-400 text-xs px-2 py-1 rounded-full font-bold">
                          {event.price.toLocaleString()} TL
                        </span>
                      </div>
                      <p className="text-purple-300 text-xs mb-2">{event.venue} • {event.category}</p>
                      {event.summary && (
                        <p className="text-purple-400 text-xs italic">"{event.summary}"</p>
                      )}
                      <div className="flex items-center gap-1 mt-2">
                        <span className="text-yellow-400 text-xs">AI Score:</span>
                        <span className="text-white text-xs font-bold">{event.quality_score}/10</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Main Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Left: Category Price Analysis */}
            <motion.div
              variants={cardVariants}
              className="lg:col-span-2 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6 hover:border-purple-500/30 transition-all"
            >
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="font-semibold text-xl text-white flex items-center gap-2">
                    <TrendingUp size={20} className="text-purple-400" />
                    Category Price Analysis
                  </h3>
                  <p className="text-purple-300 text-sm mt-1">Mean vs Median prices by category</p>
                </div>
              </div>
              <div className="h-[350px] w-full min-h-[350px]">
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={topCategories}>
                    <defs>
                      <linearGradient id="meanGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#764ba2" stopOpacity={0.6} />
                      </linearGradient>
                      <linearGradient id="medianGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f093fb" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#4facfe" stopOpacity={0.6} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                      dataKey="name"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#c4b5fd', fontSize: 11 }}
                      angle={-45}
                      textAnchor="end"
                      height={100}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#c4b5fd', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'rgba(30, 20, 60, 0.95)',
                        border: '1px solid rgba(167, 139, 250, 0.3)',
                        borderRadius: '12px',
                        color: '#fff',
                        backdropFilter: 'blur(10px)'
                      }}
                      itemStyle={{ color: '#c4b5fd' }}
                    />
                    <Bar dataKey="mean_price" fill="url(#meanGradient)" radius={[8, 8, 0, 0]} name="Mean Price" />
                    <Bar dataKey="median_price" fill="url(#medianGradient)" radius={[8, 8, 0, 0]} name="Median Price" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Right: Pie Chart - Event Distribution */}
            <motion.div
              variants={cardVariants}
              className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6 hover:border-purple-500/30 transition-all"
            >
              <h3 className="font-semibold text-xl text-white mb-6 flex items-center gap-2">
                <PieChartIcon size={20} className="text-purple-400" />
                Event Distribution
              </h3>
              <div className="h-[280px] min-h-[280px]">
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="count"
                      label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {pieData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: 'rgba(30, 20, 60, 0.95)',
                        border: '1px solid rgba(167, 139, 250, 0.3)',
                        borderRadius: '12px',
                        backdropFilter: 'blur(10px)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {pieData.map((cat, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center justify-between text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                      />
                      <span className="text-purple-200">{cat.name}</span>
                    </div>
                    <span className="text-white font-semibold">{cat.count.toLocaleString()}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Data Quality Gauge */}
          <motion.div
            variants={cardVariants}
            className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl p-6 hover:border-purple-500/30 transition-all"
          >
            <h3 className="font-semibold text-xl text-white mb-6 flex items-center gap-2">
              <CheckCircle2 size={20} className="text-purple-400" />
              Data Quality Score
            </h3>
            <div className="flex flex-col items-center justify-center h-[300px]">
              {/* Semi-circle gauge */}
              <div className="relative w-64 h-32">
                <svg viewBox="0 0 200 100" className="w-full h-full">
                  {/* Background arc */}
                  <path
                    d="M 10 100 A 90 90 0 0 1 190 100"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="20"
                    strokeLinecap="round"
                  />
                  {/* Progress arc */}
                  <motion.path
                    d="M 10 100 A 90 90 0 0 1 190 100"
                    fill="none"
                    stroke="url(#qualityGradient)"
                    strokeWidth="20"
                    strokeLinecap="round"
                    strokeDasharray={`${(dataQuality || 0) * 2.83} 283`}
                    initial={{ strokeDasharray: "0 283" }}
                    animate={{ strokeDasharray: `${(dataQuality || 0) * 2.83} 283` }}
                    transition={{ duration: 2, ease: "easeOut" }}
                  />
                  <defs>
                    <linearGradient id="qualityGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#00f2fe" />
                      <stop offset="50%" stopColor="#667eea" />
                      <stop offset="100%" stopColor="#43e97b" />
                    </linearGradient>
                  </defs>
                </svg>
                {/* Center percentage */}
                <div className="absolute inset-0 flex items-end justify-center pb-2">
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.5, type: "spring" }}
                    className="text-center"
                  >
                    <div className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-green-400 bg-clip-text text-transparent">
                      {dataQuality || 0}%
                    </div>
                  </motion.div>
                </div>
              </div>

              {/* Stats below gauge */}
              <div className="mt-8 text-center space-y-2">
                <p className="text-purple-200 text-sm">Data Completeness</p>
                <div className="flex items-center gap-4 justify-center text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-400"></div>
                    <span className="text-purple-300">Clean: {dataQuality || 0}%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-red-400"></div>
                    <span className="text-purple-300">Anomalies: {analysis.anomalies.rate}%</span>
                  </div>
                </div>
                <p className="text-purple-400 text-xs mt-3">
                  {analysis.anomalies.total.toLocaleString()} anomalies detected
                </p>
              </div>
            </div>
          </motion.div>


          {/* Category Statistics Table */}
          <motion.div
            variants={cardVariants}
            className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden hover:border-purple-500/30 transition-all"
          >
            <div className="px-6 py-5 border-b border-white/10">
              <h3 className="font-semibold text-xl text-white">Detailed Category Statistics</h3>
              <p className="text-purple-300 text-sm mt-1">
                Distribution: {analysis.distribution.shape} |
                Skewness: {analysis.distribution.skewness} |
                Normality: {analysis.normality.conclusion}
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-white/5 text-purple-300 font-semibold">
                  <tr>
                    <th className="px-6 py-4 text-left">Category</th>
                    <th className="px-6 py-4 text-right">Events</th>
                    <th className="px-6 py-4 text-right">Mean Price</th>
                    <th className="px-6 py-4 text-right">Median Price</th>
                    <th className="px-6 py-4 text-right">Std Dev (σ)</th>
                    <th className="px-6 py-4 text-right">Min</th>
                    <th className="px-6 py-4 text-right">Max</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {topCategories.map((cat, i) => (
                    <motion.tr
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      whileHover={{ backgroundColor: 'rgba(255,255,255,0.05)' }}
                      className="transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: COLORS[i % COLORS.length] }}
                          />
                          <span className="font-medium text-white">{cat.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right text-purple-200 font-semibold">{cat.count.toLocaleString()}</td>
                      <td className="px-6 py-4 text-right text-white font-semibold">{cat.mean_price.toFixed(0)} TL</td>
                      <td className="px-6 py-4 text-right text-purple-200">{cat.median_price.toFixed(0)} TL</td>
                      <td className="px-6 py-4 text-right text-purple-300">{cat.std_dev.toFixed(0)}</td>
                      <td className="px-6 py-4 text-right text-purple-300">{cat.min_price.toFixed(0)}</td>
                      <td className="px-6 py-4 text-right text-purple-300">{cat.max_price.toFixed(0)}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Advanced Analytics Section */}
          {advancedAnalysis && (
            <motion.div
              variants={cardVariants}
              className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden hover:border-purple-500/30 transition-all"
            >
              <div className="px-6 py-5 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-blue-500/10">
                <h3 className="font-semibold text-xl text-white flex items-center gap-2">
                  📈 Advanced Analytics
                </h3>
                <p className="text-purple-300 text-sm mt-1">
                  Time series trends, price segmentation, and temporal patterns
                </p>
              </div>

              <div className="p-6 space-y-6">
                {/* Time Series Chart */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white/5 rounded-xl p-5">
                    <h4 className="text-lg font-semibold text-white mb-4">📅 Events Over Time (Weekly)</h4>
                    <ResponsiveContainer width="100%" height={250}>
                      <AreaChart data={advancedAnalysis.time_series || []}>
                        <defs>
                          <linearGradient id="eventsGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#667eea" stopOpacity={0.1} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis
                          dataKey="week"
                          stroke="#a78bfa"
                          tick={{ fill: '#a78bfa', fontSize: 10 }}
                          tickFormatter={(val) => val.split('-')[1]}
                        />
                        <YAxis stroke="#a78bfa" tick={{ fill: '#a78bfa', fontSize: 10 }} />
                        <Tooltip
                          contentStyle={{ backgroundColor: 'rgba(15,15,35,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: '12px' }}
                          labelStyle={{ color: '#a78bfa' }}
                        />
                        <Area type="monotone" dataKey="events" stroke="#667eea" fill="url(#eventsGrad)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Price Segmentation */}
                  <div className="bg-white/5 rounded-xl p-5">
                    <h4 className="text-lg font-semibold text-white mb-4">💰 Price Segmentation</h4>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={advancedAnalysis.price_segments || []}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={5}
                        >
                          {(advancedAnalysis.price_segments || []).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={['#43e97b', '#4facfe', '#f093fb', '#fa709a'][index % 4]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: 'rgba(15,15,35,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: '12px' }}
                          formatter={(value, name, props) => [`${value} events (avg: ${props.payload.avg} TL)`, name]}
                        />
                        <Legend
                          formatter={(value, entry) => <span style={{ color: '#a78bfa' }}>{value}</span>}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="grid grid-cols-4 gap-2 mt-2 text-xs text-center">
                      {(advancedAnalysis.price_segments || []).map((seg, i) => (
                        <div key={i} className="text-purple-300">
                          <p className="font-bold text-white">{seg.value}</p>
                          <p>{seg.range}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Day of Week Analysis */}
                <div className="bg-white/5 rounded-xl p-5">
                  <h4 className="text-lg font-semibold text-white mb-4">📊 Events by Day of Week (with Avg Price)</h4>
                  <ResponsiveContainer width="100%" height={250}>
                    <ComposedChart data={advancedAnalysis.day_of_week || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="day" stroke="#a78bfa" tick={{ fill: '#a78bfa' }} />
                      <YAxis yAxisId="left" stroke="#667eea" tick={{ fill: '#667eea' }} />
                      <YAxis yAxisId="right" orientation="right" stroke="#f093fb" tick={{ fill: '#f093fb' }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(15,15,35,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: '12px' }}
                      />
                      <Legend />
                      <Bar yAxisId="left" dataKey="events" fill="#667eea" name="Events" radius={[4, 4, 0, 0]} />
                      <Line yAxisId="right" type="monotone" dataKey="avg_price" stroke="#f093fb" name="Avg Price (TL)" strokeWidth={3} dot={{ fill: '#f093fb' }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>

                {/* Scatter Plot: Price vs AI Quality */}
                {scatterData.length > 0 && (
                  <div className="bg-white/5 rounded-xl p-5">
                    <h4 className="text-lg font-semibold text-white mb-2">🎯 Price vs AI Quality Score</h4>
                    <p className="text-purple-400 text-xs mb-4">Each dot = 1 event. Higher = better AI summary quality. Price capped at 3000 TL.</p>
                    <ResponsiveContainer width="100%" height={300}>
                      <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis
                          type="number"
                          dataKey="price"
                          name="Price"
                          unit=" TL"
                          stroke="#a78bfa"
                          tick={{ fill: '#a78bfa', fontSize: 11 }}
                          domain={[0, 3000]}
                          tickCount={7}
                        />
                        <YAxis
                          type="number"
                          dataKey="quality"
                          name="Quality"
                          stroke="#a78bfa"
                          tick={{ fill: '#a78bfa', fontSize: 11 }}
                          domain={[0, 10]}
                          tickCount={6}
                        />
                        <ZAxis range={[80, 80]} />
                        <Tooltip
                          cursor={{ strokeDasharray: '3 3' }}
                          contentStyle={{ backgroundColor: 'rgba(15,15,35,0.95)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: '12px' }}
                          formatter={(value, name) => [name === 'Price' ? `${value} TL` : `${value}/10`, name]}
                        />
                        <Scatter
                          name="Events"
                          data={scatterData.filter(d => d.price <= 3000)}
                          fillOpacity={0.6}
                        >
                          {scatterData.filter(d => d.price <= 3000).map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={entry.quality >= 8 ? '#43e97b' : entry.quality >= 6 ? '#4facfe' : '#f093fb'}
                            />
                          ))}
                        </Scatter>
                      </ScatterChart>
                    </ResponsiveContainer>
                    <div className="flex justify-center gap-6 mt-3 text-xs text-purple-300">
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-400"></span> High (8-10)</span>
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-blue-400"></span> Medium (6-7)</span>
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-pink-400"></span> Lower (&lt;6)</span>
                    </div>
                  </div>
                )}

                {/* Category Correlation Table */}
                {advancedAnalysis.category_correlation && advancedAnalysis.category_correlation.length > 0 && (
                  <div className="bg-white/5 rounded-xl p-5 overflow-x-auto">
                    <h4 className="text-lg font-semibold text-white mb-4">🔗 Category-Price Correlation</h4>
                    <table className="w-full text-sm">
                      <thead className="text-purple-300 border-b border-white/10">
                        <tr>
                          <th className="px-3 py-2 text-left">Category</th>
                          <th className="px-3 py-2 text-right">Count</th>
                          <th className="px-3 py-2 text-right">Mean</th>
                          <th className="px-3 py-2 text-right">Median</th>
                          <th className="px-3 py-2 text-right">Std Dev</th>
                          <th className="px-3 py-2 text-right">Range</th>
                        </tr>
                      </thead>
                      <tbody>
                        {advancedAnalysis.category_correlation.map((cat, i) => (
                          <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                            <td className="px-3 py-2 text-white font-medium">{cat.category}</td>
                            <td className="px-3 py-2 text-right text-purple-200">{cat.count}</td>
                            <td className="px-3 py-2 text-right text-cyan-400">{cat.mean} TL</td>
                            <td className="px-3 py-2 text-right text-purple-200">{cat.median} TL</td>
                            <td className="px-3 py-2 text-right text-purple-300">{cat.std}</td>
                            <td className="px-3 py-2 text-right text-purple-400">{cat.min}-{cat.max} TL</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Statistical Analysis Report Section */}
          <motion.div
            variants={cardVariants}
            className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl overflow-hidden hover:border-purple-500/30 transition-all"
          >
            <div className="px-6 py-5 border-b border-white/10 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
              <h3 className="font-semibold text-xl text-white flex items-center gap-2">
                📊 Statistical Analysis Report
              </h3>
              <p className="text-purple-300 text-sm mt-1">
                Comprehensive statistical analysis powered by scipy, numpy, and pandas
              </p>
            </div>

            <div className="p-6 space-y-6">
              {/* Descriptive Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/5 rounded-xl p-5">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    📈 Descriptive Statistics
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Sample Size (n)</span>
                      <span className="text-white font-mono font-bold">{analysis.summary.total_events.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Mean (μ)</span>
                      <span className="text-white font-mono font-bold">{analysis.summary.mean_price.toFixed(2)} TL</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Median (M)</span>
                      <span className="text-white font-mono font-bold">{analysis.summary.median_price.toFixed(2)} TL</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Std Deviation (σ)</span>
                      <span className="text-white font-mono font-bold">{analysis.summary.std_dev.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Range</span>
                      <span className="text-white font-mono font-bold">{analysis.summary.min_price.toFixed(0)} - {analysis.summary.max_price.toFixed(0)} TL</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-5">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    📐 Distribution Analysis
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Distribution Shape</span>
                      <span className="text-yellow-400 font-semibold text-sm">{analysis.distribution.shape}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Skewness (γ₁)</span>
                      <span className="text-white font-mono font-bold">{analysis.distribution.skewness.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Kurtosis (γ₂)</span>
                      <span className="text-white font-mono font-bold">{analysis.distribution.kurtosis.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">IQR (Q3 - Q1)</span>
                      <span className="text-white font-mono font-bold">{analysis.distribution.iqr.toFixed(2)} TL</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/10">
                      <span className="text-purple-300">Quartiles (Q1, Q3)</span>
                      <span className="text-white font-mono font-bold">{analysis.distribution.q1.toFixed(0)}, {analysis.distribution.q3.toFixed(0)} TL</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Normality Test & Anomaly Detection */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/5 rounded-xl p-5">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    🧪 Normality Test
                  </h4>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full ${analysis.normality.is_normal ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                      <span className="text-white font-semibold">
                        {analysis.normality.is_normal ? 'Normal Distribution' : 'Non-Normal Distribution'}
                      </span>
                    </div>
                    <p className="text-purple-300 text-sm bg-white/5 p-3 rounded-lg">
                      <strong>Conclusion:</strong> {analysis.normality.conclusion}
                    </p>
                    <div className="text-purple-400 text-xs">
                      <p>• Kolmogorov-Smirnov test applied</p>
                      <p>• α = 0.05 significance level</p>
                      <p>• H₀: Data follows normal distribution</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-5">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    🔍 Anomaly Detection
                  </h4>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-red-400">{analysis.anomalies.total}</p>
                        <p className="text-purple-300 text-xs">Total Anomalies</p>
                      </div>
                      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 text-center">
                        <p className="text-3xl font-bold text-yellow-400">{analysis.anomalies.rate}%</p>
                        <p className="text-purple-300 text-xs">Anomaly Rate</p>
                      </div>
                    </div>
                    <div className="text-purple-400 text-xs">
                      <p>• IQR method: Q1 - 1.5×IQR, Q3 + 1.5×IQR</p>
                      <p>• Z-score method: |z| &gt; 3</p>
                      <p>• Price outliers detected: {analysis.anomalies.price_outliers}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Analysis Methods Used */}
              <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl p-5 border border-purple-500/20">
                <h4 className="text-lg font-semibold text-white mb-3">📚 Statistical Methods Used</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <p className="text-purple-200 font-mono">scipy.stats</p>
                    <p className="text-purple-400">Normality Tests</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <p className="text-purple-200 font-mono">pandas</p>
                    <p className="text-purple-400">Data Processing</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <p className="text-purple-200 font-mono">numpy</p>
                    <p className="text-purple-400">Numerical Analysis</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <p className="text-purple-200 font-mono">IQR/Z-score</p>
                    <p className="text-purple-400">Outlier Detection</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

        </motion.div>
      </main>
    </div>
  )
}

const KpiCard = ({ title, value, trend, trendUp, icon, gradient }) => (
  <motion.div
    variants={cardVariants}
    whileHover={{ scale: 1.02, y: -4 }}
    className={`bg-gradient-to-br ${gradient} p-[1px] rounded-2xl shadow-2xl relative overflow-hidden group cursor-pointer`}
  >
    <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 h-full relative z-10">
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20">
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
          >
            {icon && <div className="text-white">{icon}</div>}
          </motion.div>
        </div>
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring" }}
          className={`flex items-center text-xs font-bold px-3 py-1.5 rounded-full ${trendUp
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            : 'bg-red-500/20 text-red-300 border border-red-500/30'
            }`}
        >
          {trendUp ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
          {trend}
        </motion.span>
      </div>
      <div>
        <h3 className="text-purple-300 text-sm font-medium mb-1">{title}</h3>
        <p className="text-4xl font-bold text-white tracking-tight">{value}</p>
      </div>
    </div>

    {/* Glow effect on hover */}
    <motion.div
      className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500`}
    />
  </motion.div>
)

export default App
