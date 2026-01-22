"use client"

import { motion, useScroll, useTransform, useInView } from "framer-motion"
import { useRef } from "react"

const features = [
  {
    title: "5 Player Battles",
    description: "Perfectly balanced for 5 players. Every roll matters, every decision counts.",
    number: "01",
  },
  {
    title: "Strategic Dice",
    description: "Six unique faces with different effects. Attack, heal, steal, or unleash power moves.",
    number: "02",
  },
  {
    title: "Victory Points",
    description: "Earn points through survival, eliminations, and strategic plays. Highest VP wins.",
    number: "03",
  },
  {
    title: "Fallen Players",
    description: "Death isn't the end. Eliminated players become kingmakers with shadow abilities.",
    number: "04",
  },
  {
    title: "No Idle Moments",
    description: "Everyone plays until the end. Eliminated? You still roll and influence the game.",
    number: "05",
  },
  {
    title: "Dynamic Rankings",
    description: "Live rankings based on VP, HP, and survival. Anyone can clinch Top 3.",
    number: "06",
  },
]

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{
        duration: 0.5,
        delay: index * 0.1,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      className="group relative"
    >
      <div className="relative h-full p-8 rounded-2xl bg-white border border-neutral-100 hover:border-neutral-200 hover:shadow-xl hover:shadow-neutral-100/50 transition-all duration-500">
        {/* Large number background */}
        <span
          className="absolute -top-4 -right-2 text-[120px] font-bold text-neutral-50 leading-none select-none transition-all duration-500 group-hover:text-orange-50"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          {feature.number}
        </span>

        <div className="relative z-10">
          <span className="text-[10px] font-bold text-orange-500/70 tracking-[0.2em] uppercase mb-4 block">
            {feature.number}
          </span>

          <h3
            className="text-xl font-bold mb-3 text-neutral-900 group-hover:text-orange-600 transition-colors duration-300"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            {feature.title}
          </h3>
          <p className="text-neutral-500 leading-relaxed text-sm">
            {feature.description}
          </p>
        </div>
      </div>
    </motion.div>
  )
}

export function FeaturesSection() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0])

  return (
    <section id="features" className="py-32 px-4 relative overflow-hidden bg-[#fafafa]" ref={containerRef}>
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          style={{ opacity }}
          className="text-center mb-20"
        >
          <motion.span
            className="inline-block text-orange-500 text-sm tracking-[0.3em] uppercase mb-4 font-medium"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Why Play
          </motion.span>

          <motion.h2
            className="text-5xl md:text-7xl font-bold text-neutral-900 text-depth"
            style={{ fontFamily: "var(--font-heading)" }}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.1 }}
          >
            DO or DICE
          </motion.h2>

          <motion.div
            className="w-24 h-1 bg-gradient-to-r from-transparent via-orange-400 to-transparent mx-auto mt-6"
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.3 }}
          />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}
