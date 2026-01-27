"use client"

import { motion, useInView, useScroll, useTransform } from "framer-motion"
import { useRef } from "react"
import { Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export function DownloadSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  })

  const rotate = useTransform(scrollYProgress, [0, 1], [0, 30])

  return (
    <section id="download" className="py-32 px-4 relative overflow-hidden bg-white">
      {/* Subtle gradient background */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-t from-orange-50 to-transparent rounded-full blur-3xl opacity-50" />

      <div className="max-w-4xl mx-auto relative z-10" ref={ref}>
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          {/* Floating logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-12"
          >
            <motion.div
              style={{ rotate }}
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            >
              <Image
                src="/images/logo.png"
                alt="DO or DICE"
                width={160}
                height={160}
                className="mx-auto drop-shadow-2xl"
              />
            </motion.div>
          </motion.div>

          {/* Title */}
          <motion.span
            className="inline-block text-orange-500 text-sm tracking-[0.3em] uppercase mb-4 font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            Get Started
          </motion.span>

          <motion.h2
            className="text-5xl md:text-7xl font-bold text-neutral-900 mb-6 text-depth"
            style={{ fontFamily: "var(--font-heading)" }}
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Ready to Roll?
          </motion.h2>

          <motion.p
            className="text-lg text-neutral-500 max-w-xl mx-auto mb-12"
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            Download now and let the dice decide your fate.
            Gather your crew - it's time to prove who rules the table.
          </motion.p>

          {/* Download button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mb-16"
          >
            <Button
              size="lg"
              className="bg-neutral-900 hover:bg-neutral-800 text-white px-12 py-8 text-xl font-semibold gap-3 group rounded-full shadow-2xl shadow-neutral-900/20 hover:shadow-neutral-900/30 transition-all duration-300 hover:scale-105 btn-premium"
              asChild
            >
              <a href="/DoOrDice.zip" download>
                <Download className="w-6 h-6 group-hover:-translate-y-1 transition-transform" />
                Download for Windows
              </a>
            </Button>
            <p className="text-sm text-neutral-400 mt-4">
              v0.1.0 <span className="text-orange-400">•</span> Free to play <span className="text-orange-400">•</span> ~50MB
            </p>
          </motion.div>

          {/* Requirements */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="flex flex-wrap justify-center gap-8 mb-16"
          >
            {[
              { label: "Platform", value: "Windows 10+" },
              { label: "Python", value: "3.13+ (bundled)" },
              { label: "Storage", value: "~50 MB" },
            ].map((req) => (
              <div key={req.label} className="text-center">
                <p className="text-xs text-neutral-400 uppercase tracking-wider mb-1">{req.label}</p>
                <p className="text-neutral-700 font-medium">{req.value}</p>
              </div>
            ))}
          </motion.div>

          {/* Source code */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="p-8 rounded-3xl border border-neutral-100 bg-neutral-50"
          >
            <h4
              className="font-semibold text-neutral-900 mb-3"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              Build from Source
            </h4>
            <p className="text-sm text-neutral-500 mb-6">
              Clone and run with Python for development
            </p>
            <div className="bg-neutral-900 rounded-xl p-4 text-left font-mono text-sm overflow-x-auto">
              <div className="space-y-1 text-neutral-300">
                <p><span className="text-orange-400">git</span> clone https://github.com/Paurakh977/DO-OR-DICE.git</p>
                <p><span className="text-orange-400">cd</span> DO-OR-DICE</p>
                <p><span className="text-orange-400">uv</span> sync</p>
                <p><span className="text-orange-400">uv</span> run main.py</p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
