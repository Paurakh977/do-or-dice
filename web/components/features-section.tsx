"use client"

import { motion, useScroll, useTransform, useInView, useMotionValue, useSpring } from "framer-motion"
import { useRef, MouseEvent } from "react"
import { Flame, Star, Shield, Skull, Zap, Trophy, Users, Dna, Activity } from "lucide-react"

const features = [
  {
    title: "5-Player Chaos",
    description: "Balanced ecosystem. Every decision creates ripples. 1 vs 4 or free-for-all?",
    icon: Users,
    color: "from-orange-400 to-red-600"
  },
  {
    title: "Tactical Dice",
    description: "Six unique faces. Attack, heal, steal, or risk it all for a Power Move.",
    icon: Dna,
    color: "from-amber-400 to-orange-600"
  },
  {
    title: "Victory Points",
    description: "Survival is currency. Eliminate foes or outlast them to stack VP.",
    icon: Trophy,
    color: "from-yellow-400 to-amber-600"
  },
  {
    title: "Fallen Ghosts",
    description: "Death awaits, but it is not the end. Haunt the living from the shadows.",
    icon: Skull,
    color: "from-red-500 to-rose-900"
  },
  {
    title: "Live Reaction",
    description: "No downtime. Defend yourself even when it's not your turn.",
    icon: Activity,
    color: "from-orange-300 to-red-500"
  },
  {
    title: "Kingmaker",
    description: "The Fallen decide the winner. Bargain for your life.",
    icon: Star,
    color: "from-rose-400 to-red-700"
  },
]

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const ref = useRef<HTMLDivElement>(null)

  // 3D Tilt Logic
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const mouseX = useSpring(x, { stiffness: 500, damping: 100 })
  const mouseY = useSpring(y, { stiffness: 500, damping: 100 })

  function onMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top, width, height } = currentTarget.getBoundingClientRect()
    x.set(clientX - left - width / 2)
    y.set(clientY - top - height / 2)
  }

  function onMouseLeave() {
    x.set(0)
    y.set(0)
  }

  const rotateX = useTransform(mouseY, [-300, 300], [5, -5])
  const rotateY = useTransform(mouseX, [-300, 300], [-5, 5])
  const opacity = useTransform(mouseX, [-300, 300], [0, 1])

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50, rotateX: 10 }}
      whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
      viewport={{ once: true, margin: "-10%" }}
      transition={{
        duration: 0.8,
        delay: index * 0.1,
        ease: [0.21, 0.47, 0.32, 0.98]
      }}
      className="group relative h-full perspective-1000"
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      style={{ perspective: 1000 }}
    >
      <motion.div
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className="relative h-full p-8 rounded-3xl bg-[#0a0a0a] border border-neutral-900 overflow-hidden shadow-2xl shadow-black/50"
      >
        {/* Texture Overlay */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none z-0"
          style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }}
        />

        {/* Dynamic Glow */}
        <motion.div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-0"
          style={{
            background: `radial-gradient(600px circle at ${mouseX}px ${mouseY}px, rgba(255,255,255,0.03), transparent 40%)`
          }}
        />

        {/* Content Container with slight Z-index for depth */}
        <div className="relative z-10 flex flex-col h-full transform-style-3d translate-z-10">

          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div className={`p-3 rounded-2xl bg-gradient-to-br from-neutral-900 to-black border border-neutral-800 text-neutral-400 group-hover:text-orange-500 group-hover:border-orange-500/20 group-hover:shadow-[0_0_30px_-10px_rgba(249,115,22,0.3)] transition-all duration-500`}>
              <feature.icon className="w-6 h-6" />
            </div>
            <span className="text-neutral-800 font-mono text-xs tracking-widest group-hover:text-orange-900/50 transition-colors">
              0{index + 1}
            </span>
          </div>

          <div className="mt-auto space-y-4">
            <h3
              className="text-2xl font-medium text-white group-hover:translate-x-1 transition-transform duration-300"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              {feature.title}
            </h3>
            <p className="text-neutral-500 text-sm leading-relaxed group-hover:text-neutral-400 transition-colors duration-300">
              {feature.description}
            </p>
          </div>
        </div>

        {/* Bottom animated border/glow */}
        <div className={`absolute bottom-0 left-0 h-[1px] w-full bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-100 transition-opacity duration-700 ease-out`} />
        <div className={`absolute bottom-0 left-0 h-[200px] w-full bg-gradient-to-t ${feature.color} to-transparent opacity-0 group-hover:opacity-5 transition-opacity duration-700 ease-out pointer-events-none`} />

      </motion.div>
    </motion.div>
  )
}

export function FeaturesSection() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [0, -100])
  const y2 = useTransform(scrollYProgress, [0, 1], [0, -200])
  const columnY = useTransform(scrollYProgress, [0, 1], [20, -40]) // Middle column moves faster/slower - reduced to prevent overlap
  const headerY = useTransform(scrollYProgress, [0, 0.3], [100, 0])

  return (
    <section id="features" className="py-32 px-6 relative bg-black overflow-hidden bg-[url('/noise.png')] bg-repeat" ref={containerRef}>
      {/* Ambient Background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full pointer-events-none">
        <motion.div style={{ y }} className="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-orange-900/10 rounded-full blur-[120px]" />
        <motion.div style={{ y: y2 }} className="absolute bottom-[20%] right-[10%] w-[400px] h-[400px] bg-red-900/10 rounded-full blur-[100px]" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div
          style={{ y: headerY }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-24 md:mb-32 flex flex-col md:flex-row md:items-end justify-between gap-8"
        >
          <div className="max-w-xl">
            <span className="text-orange-500 font-mono text-xs tracking-[0.2em] uppercase mb-4 block">
              Core Mechanics
            </span>
            <h2
              className="text-5xl md:text-7xl font-bold text-white tracking-tight leading-[0.9]"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              ENGINEERED FOR <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-600">
                CHAOS.
              </span>
            </h2>
          </div>
          <p className="text-neutral-500 max-w-sm text-sm leading-relaxed md:text-right">
            Minimal luck. Maximum psychology. The dice decide the action, but you decide the outcome.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          <div className="space-y-6 md:space-y-8">
            {features.filter((_, i) => i % 3 === 0).map((feature, i) => (
              <FeatureCard key={feature.title} feature={feature} index={i * 3} />
            ))}
          </div>
          <motion.div style={{ y: columnY }} className="space-y-6 md:space-y-8">
            {features.filter((_, i) => i % 3 === 1).map((feature, i) => (
              <FeatureCard key={feature.title} feature={feature} index={i * 3 + 1} />
            ))}
          </motion.div>
          <div className="space-y-6 md:space-y-8">
            {features.filter((_, i) => i % 3 === 2).map((feature, i) => (
              <FeatureCard key={feature.title} feature={feature} index={i * 3 + 2} />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
