"use client"

import { motion, useInView, useMotionValue, useSpring, useTransform, useScroll } from "framer-motion"
import { useRef, useState } from "react"
import { cn } from "@/lib/utils"
import { Dice1, Dice2, Dice3, Dice4, Dice5, Dice6 } from "lucide-react"

const diceEffects = [
  { face: 1, name: "BACKFIRE", effect: "-3 HP", target: "Self", color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20", icon: Dice1 },
  { face: 2, name: "JAB", effect: "-2 HP", target: "Target", color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/20", icon: Dice2 },
  { face: 3, name: "STEAL", effect: "+1 VP", target: "Pickpocket", color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: Dice3 },
  { face: 4, name: "STRIKE", effect: "-4 HP", target: "Target", color: "text-orange-500", bg: "bg-orange-600/10", border: "border-orange-600/20", icon: Dice4 },
  { face: 5, name: "RECOVER", effect: "+3 HP", target: "Heal", color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: Dice5 },
  { face: 6, name: "POWER", effect: "CLUTCH", target: "-6HP / +3VP", color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/20", icon: Dice6 },
]

function DiceCard({ dice, index }: { dice: typeof diceEffects[0]; index: number }) {
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

  const rotateX = useTransform(mouseY, [-200, 200], [10, -10])
  const rotateY = useTransform(mouseX, [-200, 200], [-10, 10])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      whileInView={{ opacity: 1, scale: 1, y: 0 }}
      viewport={{ once: true, margin: "-10%" }}
      transition={{ delay: index * 0.05, duration: 0.5 }}
      style={{ perspective: 1000 }}
      className="group relative h-full"
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
    >
      <motion.div
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className={`relative h-full p-6 rounded-2xl border border-neutral-800 bg-[#0a0a0a] overflow-hidden transition-colors hover:border-neutral-700 shadow-lg shadow-black/50`}
      >
        {/* Noise Texture */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none z-0"
          style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }}
        />

        {/* Subtle Gradient Background based on dice type */}
        <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500 bg-gradient-to-br ${dice.color.replace('text-', 'from-')} to-transparent`} />

        <div className="relative z-10 flex flex-col h-full justify-between transform-style-3d translate-z-10">
          <div className="flex justify-between items-start mb-4">
            <div className="flex flex-col">
              <span className={`text-[10px] font-bold tracking-[0.2em] ${dice.color} mb-1 opacity-80 uppercase`}>{dice.name}</span>
              <span className="text-xl font-bold text-white mb-2 tracking-tight">{dice.effect}</span>
              <span className="text-[10px] text-neutral-500 border border-neutral-800 bg-neutral-900/50 px-2 py-0.5 rounded-full inline-block w-fit uppercase tracking-wider">{dice.target}</span>
            </div>
            <div className={`p-2 rounded-xl bg-neutral-900/50 border border-neutral-800 ${dice.color} group-hover:scale-110 transition-transform duration-300`}>
              <dice.icon size={20} />
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export function RulesSection() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  })

  // Parallax Values
  const titleY = useTransform(scrollYProgress, [0, 0.5], [50, 0])
  const gridY = useTransform(scrollYProgress, [0, 1], [100, -100])
  const fallenY = useTransform(scrollYProgress, [0, 1], [150, -50])

  return (
    <section id="rules" className="py-32 px-6 bg-[#0a0a0a] relative overflow-hidden text-neutral-200" ref={containerRef}>
      <div className="max-w-7xl mx-auto relative z-10">

        {/* Section Header */}
        <div className="flex flex-col md:flex-row gap-12 mb-20">
          <motion.div
            style={{ y: titleY }}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            className="flex-1"
          >
            <h2 className="text-6xl md:text-8xl font-black text-white mb-6 tracking-tighter" style={{ fontFamily: "var(--font-heading)" }}>
              THE <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-600">CODEX</span>
            </h2>
          </motion.div>

          <motion.div
            style={{ y: useTransform(scrollYProgress, [0, 0.5], [100, 0]) }}
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="flex-1 space-y-6 pt-4"
          >
            <div className="flex gap-4 p-6 rounded-2xl bg-neutral-900 border border-neutral-800">
              <div className="space-y-1">
                <p className="text-sm text-neutral-500 uppercase tracking-widest">Victory Condition</p>
                <p className="text-xl font-medium text-white">Survivor or 12 Rounds</p>
              </div>
              <div className="w-px bg-neutral-800" />
              <div className="space-y-1">
                <p className="text-sm text-neutral-500 uppercase tracking-widest">Ranking</p>
                <p className="text-xl font-medium text-orange-500">VP &gt; HP &gt; Roll</p>
              </div>
            </div>
            <p className="text-neutral-500 leading-relaxed">
              Rules are simple: Roll high, act fast, and don't die. The game ends when only one player remains or the round limit is reached.
            </p>
          </motion.div>
        </div>

        {/* Dice Grid - Staggered Parallax */}
        <motion.div style={{ y: gridY }} className="mb-20">
          <h3 className="text-sm font-mono text-neutral-500 mb-8 uppercase tracking-widest pl-2">Dice Permutations</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {diceEffects.map((dice, index) => (
              <motion.div
                key={dice.face}
                style={{ y: useTransform(scrollYProgress, [0, 1], [0, index % 2 === 0 ? -30 : 30]) }}
              >
                <DiceCard dice={dice} index={index} />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Fallen Mechanics */}
        <motion.div style={{ y: fallenY }} className="relative group perspective-1000">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

          <div className="relative rounded-3xl bg-[#0a0a0a] border border-neutral-800 p-8 md:p-12 overflow-hidden shadow-2xl">
            {/* Noise Texture */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none z-0"
              style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }}
            />

            <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-purple-900/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
              <div>
                <span className="text-purple-500 font-mono text-xs tracking-widest uppercase mb-2 block">Post-Mortem Gameplay</span>
                <h3 className="text-3xl font-bold text-white mb-2" style={{ fontFamily: "var(--font-heading)" }}>Fallen Protocols</h3>
                <p className="text-neutral-400 max-w-lg leading-relaxed text-sm">Even in death, you serve. Roll as a ghost to bless your allies or curve your enemies' fate. The game doesn't end when your heart stops.</p>
              </div>

              <div className="flex gap-4">
                <div className="text-center p-5 bg-neutral-900/50 rounded-2xl border border-neutral-800 min-w-[110px] group/stat hover:border-emerald-500/30 transition-colors">
                  <span className="block text-3xl font-bold text-emerald-500 mb-1 group-hover/stat:scale-110 transition-transform">3-4</span>
                  <span className="text-[10px] uppercase text-neutral-500 tracking-widest font-mono">Blessing</span>
                </div>
                <div className="text-center p-5 bg-neutral-900/50 rounded-2xl border border-neutral-800 min-w-[110px] group/stat hover:border-red-500/30 transition-colors">
                  <span className="block text-3xl font-bold text-red-500 mb-1 group-hover/stat:scale-110 transition-transform">5-6</span>
                  <span className="text-[10px] uppercase text-neutral-500 tracking-widest font-mono">Curse</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>


    </section >
  )
}
