"use client"

import { motion, useScroll, useTransform, useInView, useMotionValue, useSpring } from "framer-motion"
import { useRef } from "react"
import { cn } from "@/lib/utils"

const gameplaySteps = [
  {
    step: "01",
    title: "The Roll",
    subtitle: "Fate is cast",
    description: "Roll the 6-sided obsidian die. Every face holds a different power. Will you Strike, Heal, or Gamble?",
  },
  {
    step: "02",
    title: "The Action",
    subtitle: "Execute your will",
    description: "Target your enemies or bolster your defenses. The choice is yours, but the consequences are shared.",
  },
  {
    step: "03",
    title: "The Survival",
    subtitle: "Outlast the chaos",
    description: "Survive the round to earn Victory Points via passive income. Staying alive is the most profitable strategy.",
  },
  {
    step: "04",
    title: "The Afterlife",
    subtitle: "Death is power",
    description: "If you fall, you rise as a Fallen. Roll to buf allies or curse your killers. You decide who wins.",
  },
]

function GameplayStep({ step, index, isLast }: { step: typeof gameplaySteps[0]; index: number; isLast: boolean }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  // 3D Tilt Logic for the card
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

  return (
    <div ref={ref} className="relative flex gap-8 md:gap-16 group/step">
      {/* Timeline Line */}
      <div className="flex flex-col items-center">
        <motion.div
          initial={{ height: 0 }}
          animate={isInView ? { height: "100%" } : { height: 0 }}
          transition={{ duration: 1, ease: "easeInOut" }}
          className="w-px bg-gradient-to-b from-neutral-800 via-neutral-700 to-neutral-800 relative h-full group-hover/step:via-orange-500/50 transition-colors duration-500"
        >
        </motion.div>
      </div>

      {/* Content */}
      <motion.div
        className="pb-24 w-full perspective-1000"
        initial={{ opacity: 0, x: 50 }}
        animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 50 }}
        transition={{ duration: 0.8, ease: "easeOut", delay: index * 0.1 }}
      >
        <div className="flex flex-col md:flex-row md:items-start gap-8">
          <div className="relative">
            <span className="text-6xl md:text-8xl font-black text-neutral-900 select-none leading-none absolute -left-4 -top-8 -z-10 transition-colors duration-500 group-hover/step:text-neutral-800" style={{ fontFamily: "var(--font-heading)" }}>
              {step.step}
            </span>
            <h3 className="text-3xl md:text-4xl font-bold text-white mb-2 relative z-10" style={{ fontFamily: "var(--font-heading)" }}>
              {step.title}
            </h3>
            <p className="text-orange-500 text-lg md:text-xl font-medium mb-6 italic font-serif opacity-80">
              {step.subtitle}
            </p>
          </div>

          <motion.div
            className="relative w-full max-w-xl group-card"
            style={{ perspective: 1000 }}
            onMouseMove={onMouseMove}
            onMouseLeave={onMouseLeave}
          >
            <motion.div
              style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
              className="relative p-8 rounded-3xl bg-[#0a0a0a] border border-neutral-900 hover:border-neutral-800 transition-colors duration-500 shadow-2xl shadow-black/50"
            >
              {/* Texture */}
              <div className="absolute inset-0 opacity-[0.03] pointer-events-none z-0 rounded-3xl"
                style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }}
              />
              {/* Glow */}
              <div className="absolute -inset-1 bg-gradient-to-r from-orange-500/20 to-purple-500/20 rounded-3xl blur-2xl opacity-0 group-hover/card:opacity-100 transition-opacity duration-700" />

              <div className="relative z-10 transform-style-3d translate-z-10">
                <p className="text-neutral-400 text-base leading-relaxed">
                  {step.description}
                </p>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Node */}
      <motion.div
        className="absolute left-0 -translate-x-1/2 top-4 w-3 h-3 rounded-full bg-neutral-950 border border-neutral-700 z-20 shadow-[0_0_10px_rgba(0,0,0,1)]"
        initial={{ scale: 0 }}
        whileInView={{ scale: 1, borderColor: "#f97316" }}
        transition={{ duration: 0.4, delay: index * 0.1 }}
      >
        <div className="absolute inset-0 rounded-full bg-orange-500/50 opacity-0 group-hover/step:opacity-100 group-hover/step:animate-ping" />
      </motion.div>
    </div>
  )
}

export function GameplaySection() {
  const containerRef = useRef(null)

  return (
    <section id="gameplay" className="py-32 px-6 bg-[#050505] relative overflow-hidden" ref={containerRef}>
      {/* Background Elements */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,black,transparent)]" />

      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          className="mb-32 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-6xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-b from-neutral-100 to-neutral-800" style={{ fontFamily: "var(--font-heading)" }}>
            THE FLOW
          </h2>
        </motion.div>

        <div className="relative pl-4 md:pl-20">
          {gameplaySteps.map((step, index) => (
            <GameplayStep
              key={step.step}
              step={step}
              index={index}
              isLast={index === gameplaySteps.length - 1}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
