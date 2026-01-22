"use client"

import { DiceScene } from "@/components/dice-scene"
import { Button } from "@/components/ui/button"
import { ArrowRight, Flame } from "lucide-react"
import { motion } from "framer-motion"
import { useEffect, useState, useMemo } from "react"

// Dark obsidian floating rock - contrasts against light background
function ObsidianRock({
    size,
    initialX,
    initialY,
    delay,
    duration
}: {
    size: number
    initialX: number
    initialY: number
    delay: number
    duration: number
}) {
    return (
        <motion.div
            className="absolute rounded-full pointer-events-none"
            style={{
                width: size,
                height: size,
                left: `${initialX}%`,
                top: `${initialY}%`,
                background: `radial-gradient(circle at 30% 30%, 
                    rgba(60, 55, 55, 0.85) 0%, 
                    rgba(25, 20, 20, 0.9) 50%, 
                    rgba(10, 8, 8, 0.95) 100%)`,
                boxShadow: `
                    inset 0 0 ${size * 0.2}px rgba(255, 80, 40, 0.1),
                    0 ${size * 0.1}px ${size * 0.4}px rgba(0, 0, 0, 0.2),
                    0 0 ${size * 0.15}px rgba(255, 80, 40, 0.05)
                `,
            }}
            animate={{
                y: [0, -30, -15, -40, 0],
                x: [0, 10, -8, 15, 0],
                scale: [1, 1.03, 0.98, 1.02, 1],
                rotate: [0, 3, -2, 4, 0],
            }}
            transition={{
                duration: duration,
                delay: delay,
                repeat: Infinity,
                ease: "easeInOut",
            }}
        />
    )
}

// Subtle lava ember particle
function LavaEmber({ delay }: { delay: number }) {
    const [mounted, setMounted] = useState(false)
    const left = useMemo(() => `${Math.random() * 100}%`, [])
    const drift = useMemo(() => (Math.random() - 0.5) * 80, [])
    const duration = useMemo(() => 8 + Math.random() * 4, [])
    const size = useMemo(() => 2 + Math.random() * 2, [])

    useEffect(() => {
        setMounted(true)
    }, [])

    if (!mounted) return null

    return (
        <motion.div
            className="absolute rounded-full pointer-events-none"
            style={{
                width: size,
                height: size,
                left: left,
                bottom: "-5%",
                background: "radial-gradient(circle, #ff6030 0%, #ff4010 100%)",
                boxShadow: "0 0 4px #ff5020, 0 0 8px rgba(255, 80, 32, 0.5)",
            }}
            initial={{ opacity: 0, y: 0 }}
            animate={{
                y: [0, -window.innerHeight * 1.1],
                x: [0, drift],
                opacity: [0, 0.8, 0.6, 0],
                scale: [0.5, 1, 0.8, 0],
            }}
            transition={{
                duration: duration,
                delay: delay,
                repeat: Infinity,
                ease: "easeOut",
            }}
        />
    )
}

export function HeroSection() {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    // Obsidian rocks positioned around edges
    const rocks = useMemo(() => [
        { size: 60, x: 3, y: 75, delay: 0, duration: 14 },
        { size: 90, x: 88, y: 15, delay: 2, duration: 16 },
        { size: 45, x: 8, y: 25, delay: 1, duration: 12 },
        { size: 75, x: 92, y: 70, delay: 3, duration: 15 },
        { size: 35, x: 82, y: 45, delay: 0.5, duration: 13 },
        { size: 50, x: 5, y: 90, delay: 1.5, duration: 14 },
    ], [])

    return (
        <section className="relative min-h-screen w-full overflow-hidden bg-[#fafafa] selection:bg-orange-500/20">
            {/* Subtle warm gradient at bottom */}
            <div
                className="absolute bottom-0 left-0 right-0 h-[40%] pointer-events-none"
                style={{
                    background: "radial-gradient(ellipse 80% 60% at 50% 100%, rgba(255, 100, 50, 0.03) 0%, transparent 70%)"
                }}
            />

            {/* Dark obsidian floating rocks */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {mounted && rocks.map((rock, i) => (
                    <ObsidianRock
                        key={i}
                        size={rock.size}
                        initialX={rock.x}
                        initialY={rock.y}
                        delay={rock.delay}
                        duration={rock.duration}
                    />
                ))}
            </div>

            {/* Lava ember particles */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {mounted && [...Array(12)].map((_, i) => (
                    <LavaEmber key={i} delay={i * 0.7} />
                ))}
            </div>

            {/* 3D Dice Scene */}
            <div className="absolute inset-0 z-10 lg:left-[15%] lg:scale-110">
                <DiceScene />
            </div>

            {/* Content Container */}
            <div className="relative z-20 flex min-h-screen max-w-7xl mx-auto px-6 items-center">
                <div className="flex flex-col max-w-2xl gap-10">

                    {/* Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <span className="inline-flex items-center gap-3 rounded-full border border-orange-200/60 bg-white/60 backdrop-blur-sm px-4 py-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-orange-800/80 shadow-sm">
                            <span className="flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-orange-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
                            </span>
                            Volcanic Update 2.0
                        </span>
                    </motion.div>

                    {/* Typography - Clean with depth */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 0.2 }}
                    >
                        <h1
                            className="text-8xl md:text-[10rem] font-black tracking-[-0.04em] leading-[0.8] mb-6 text-depth-heavy"
                            style={{ fontFamily: "var(--font-heading)" }}
                        >
                            <span className="text-neutral-900">DO OR</span>
                            <br />
                            <span
                                className="relative inline-block"
                                style={{
                                    background: "linear-gradient(135deg, #1a1a1a 0%, #ff6040 60%, #ff4020 100%)",
                                    WebkitBackgroundClip: "text",
                                    WebkitTextFillColor: "transparent",
                                    backgroundClip: "text",
                                }}
                            >
                                DICE.
                            </span>
                        </h1>
                        <p className="text-xl text-neutral-500 max-w-md leading-relaxed font-medium tracking-tight">
                            Define your fate in a world of physics-based chaos.
                            <span className="text-neutral-800 block mt-1 font-semibold">High stakes. Zero mercy.</span>
                        </p>
                    </motion.div>

                    {/* Actions */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4 }}
                        className="flex flex-wrap items-center gap-6"
                    >
                        <Button
                            className="h-16 px-10 rounded-full bg-neutral-900 text-white font-bold text-lg hover:bg-neutral-800 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] shadow-2xl shadow-neutral-900/20 btn-premium group"
                        >
                            <Flame className="mr-2 h-5 w-5 fill-orange-500 text-orange-500 group-hover:scale-110 transition-transform" />
                            Roll the Dice
                        </Button>
                        <Button
                            variant="link"
                            className="text-neutral-700 font-bold text-lg hover:text-neutral-900 transition-all px-0 group"
                        >
                            Explore Rules
                            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                    </motion.div>

                    {/* Minimal Stats */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8, delay: 0.6 }}
                        className="flex gap-12 items-center border-t border-neutral-200/60 pt-8 mt-4"
                    >
                        <div className="flex flex-col">
                            <span
                                className="text-3xl font-black text-neutral-900"
                                style={{ fontFamily: "var(--font-heading)" }}
                            >
                                12K+
                            </span>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">
                                Active Players
                            </span>
                        </div>
                        <div className="h-8 w-px bg-neutral-200" />
                        <div className="flex flex-col">
                            <span
                                className="text-3xl font-black text-neutral-900"
                                style={{ fontFamily: "var(--font-heading)" }}
                            >
                                4.9
                            </span>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">
                                Global Rating
                            </span>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Subtle noise texture */}
            <div className="noise-overlay" />
        </section>
    )
}