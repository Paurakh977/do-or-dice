"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useState } from "react"
import { cn } from "@/lib/utils"

const diceEffects = [
  { face: 1, name: "Backfire", effect: "-3 HP", target: "Self", color: "text-red-500" },
  { face: 2, name: "Jab", effect: "-2 HP", target: "Target", color: "text-orange-500" },
  { face: 3, name: "Pickpocket", effect: "+1 VP", target: "Steal", color: "text-amber-500" },
  { face: 4, name: "Strike", effect: "-4 HP", target: "Target", color: "text-orange-600" },
  { face: 5, name: "Recover", effect: "+3 HP", target: "Self", color: "text-emerald-500" },
  { face: 6, name: "Power Move", effect: "Choice", target: "-6HP / +3VP", color: "text-amber-400" },
]

const fallenEffects = [
  { roll: "1-2", effect: "Nothing", color: "text-neutral-400" },
  { roll: "3-4", effect: "+2 HP or +1 VP to any", color: "text-emerald-500" },
  { roll: "5-6", effect: "-2 HP or -1 VP to any", color: "text-red-500" },
]

function DiceEffectRow({ dice, index }: { dice: typeof diceEffects[0]; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-50px" })
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -30 }}
      animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <div className={cn(
        "flex items-center gap-4 p-4 rounded-xl border border-neutral-100 transition-all duration-300",
        isHovered && "border-orange-200 bg-orange-50/50 shadow-lg shadow-orange-100/30"
      )}>
        {/* Dice face number */}
        <div className={cn(
          "w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-bold transition-all duration-300",
          "bg-neutral-50 border border-neutral-100",
          isHovered && "border-orange-200 bg-white scale-110"
        )} style={{ fontFamily: "var(--font-heading)" }}>
          <span className={dice.color}>{dice.face}</span>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <span className={cn("font-semibold", dice.color)} style={{ fontFamily: "var(--font-heading)" }}>
              {dice.name}
            </span>
          </div>
          <span className="text-sm text-neutral-400">{dice.target}</span>
        </div>

        {/* Effect */}
        <span className={cn("text-lg font-bold tabular-nums", dice.color)} style={{ fontFamily: "var(--font-heading)" }}>
          {dice.effect}
        </span>
      </div>
    </motion.div>
  )
}

export function RulesSection() {
  const containerRef = useRef(null)

  return (
    <section id="rules" className="py-32 px-4 relative overflow-hidden bg-[#fafafa]" ref={containerRef}>
      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          className="text-center mb-24"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <motion.span
            className="inline-block text-orange-500 text-sm tracking-[0.3em] uppercase mb-4 font-medium"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            Master the Game
          </motion.span>
          <motion.h2
            className="text-5xl md:text-7xl font-bold text-neutral-900 text-depth"
            style={{ fontFamily: "var(--font-heading)" }}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            The Rules
          </motion.h2>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          {/* Left: Setup & Win */}
          <div className="space-y-12">
            {/* Setup */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3
                className="text-2xl font-bold text-neutral-900 mb-6 flex items-center gap-3"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                <span className="w-8 h-px bg-orange-400" />
                Setup
              </h3>

              <div className="space-y-4">
                {[
                  { label: "Players", value: "5", desc: "Exactly" },
                  { label: "Starting HP", value: "20", desc: "Each" },
                  { label: "Starting VP", value: "0", desc: "Earn through play" },
                ].map((item, i) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, x: -30 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center gap-4 p-4 rounded-xl bg-white border border-neutral-100"
                  >
                    <span
                      className="text-4xl font-bold text-orange-500 w-16"
                      style={{ fontFamily: "var(--font-heading)" }}
                    >
                      {item.value}
                    </span>
                    <div>
                      <p className="font-medium text-neutral-900">{item.label}</p>
                      <p className="text-sm text-neutral-400">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Win condition */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3
                className="text-2xl font-bold text-neutral-900 mb-6 flex items-center gap-3"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                <span className="w-8 h-px bg-orange-400" />
                Victory
              </h3>

              <div className="p-6 rounded-2xl border border-neutral-100 bg-white">
                <p className="text-neutral-600 mb-4">Game ends when:</p>
                <ul className="space-y-2 text-neutral-500 mb-6">
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
                    Only 1 player remains alive
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-orange-400" />
                    12 rounds completed
                  </li>
                </ul>
                <div className="pt-4 border-t border-neutral-100">
                  <p className="text-sm text-orange-500 mb-2 font-medium">Ranking Priority:</p>
                  <p className="text-xs text-neutral-400 leading-relaxed">
                    VP → HP at elimination → Fewer fallen rounds → Final roll
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right: Dice effects */}
          <div className="space-y-12">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3
                className="text-2xl font-bold text-neutral-900 mb-6 flex items-center gap-3"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                <span className="w-8 h-px bg-orange-400" />
                Dice Effects
              </h3>

              <div className="space-y-3">
                {diceEffects.map((dice, index) => (
                  <DiceEffectRow key={dice.face} dice={dice} index={index} />
                ))}
              </div>
            </motion.div>

            {/* Fallen effects */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h3
                className="text-2xl font-bold text-neutral-900 mb-6 flex items-center gap-3"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                <span className="w-8 h-px bg-neutral-300" />
                Shadow Effects
                <span className="text-sm font-normal text-neutral-400">(Fallen)</span>
              </h3>

              <div className="grid grid-cols-3 gap-3">
                {fallenEffects.map((effect, i) => (
                  <motion.div
                    key={effect.roll}
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="p-4 rounded-xl border border-neutral-100 bg-white text-center"
                  >
                    <span
                      className="text-2xl font-bold text-neutral-800 block mb-1"
                      style={{ fontFamily: "var(--font-heading)" }}
                    >
                      {effect.roll}
                    </span>
                    <span className={cn("text-xs", effect.color)}>{effect.effect}</span>
                  </motion.div>
                ))}
              </div>
              <p className="text-xs text-neutral-400 mt-4 italic">
                Cannot affect the same player two rounds in a row.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
