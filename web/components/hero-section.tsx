"use client"

import { DiceScene } from "@/components/dice-scene"
import { Button } from "@/components/ui/button"
import { ArrowRight, Flame } from "lucide-react"

export function HeroSection() {
    return (
        <section className="relative h-screen w-full overflow-hidden bg-[#fafafa] selection:bg-orange-500 selection:text-white">

            {/* 3D Scene - Positioned for dramatic negative space */}
            <div className="absolute inset-0 z-10 lg:left-[15%] lg:scale-110">
                <DiceScene />
            </div>

            {/* Content Container */}
            <div className="relative z-20 flex h-full max-w-7xl mx-auto px-6 items-center">
                <div className="flex flex-col max-w-2xl gap-10">

                    {/* Badge */}
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
                        <span className="inline-flex items-center gap-3 rounded-full border border-orange-200 bg-white/50 backdrop-blur-md px-4 py-1.5 text-[10px] font-black uppercase tracking-[0.2em] text-orange-900 shadow-sm">
                            <span className="flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-orange-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-600"></span>
                            </span>
                            Volcanic Update 2.0
                        </span>
                    </div>

                    {/* Typography */}
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
                        <h1 className="font-heading text-8xl md:text-[10rem] font-black tracking-tighter text-neutral-950 leading-[0.8] mb-6">
                            DO OR <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-br from-black via-orange-600 to-orange-400">
                                DICE.
                            </span>
                        </h1>
                        <p className="text-xl text-neutral-500 max-w-md leading-relaxed font-medium tracking-tight">
                            Define your fate in a world of physics-based chaos.
                            <span className="text-black block mt-1">High stakes. Zero mercy.</span>
                        </p>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap items-center gap-6 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-400">
                        <Button
                            className="h-16 px-10 rounded-full bg-black text-white font-bold text-lg hover:bg-neutral-800 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-2xl shadow-black/10 group"
                        >
                            <Flame className="mr-2 h-5 w-5 fill-orange-500 text-orange-500" />
                            Roll the Dice
                        </Button>
                        <Button
                            variant="link"
                            className="text-neutral-900 font-bold text-lg decoration-2 decoration-orange-500/30 hover:decoration-orange-500 transition-all px-0"
                        >
                            Explore Rules
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </div>

                    {/* Minimal Stats */}
                    <div className="flex gap-12 items-center animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-600 border-t border-neutral-200/60 pt-8 mt-4">
                        <div className="flex flex-col">
                            <span className="text-3xl font-black text-black">12K+</span>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Active Players</span>
                        </div>
                        <div className="h-8 w-px bg-neutral-200" />
                        <div className="flex flex-col">
                            <span className="text-3xl font-black text-black">4.9</span>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Global Rating</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Background Texture Overlay */}
            <div className="pointer-events-none absolute inset-0 opacity-[0.02] z-0"
                style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.6' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")` }}
            />
        </section>
    )
}