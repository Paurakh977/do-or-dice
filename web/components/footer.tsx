"use client"

import { motion } from "framer-motion"
import { Github } from "lucide-react"
import Image from "next/image"

export function Footer() {
  return (
    <footer className="py-16 px-4 border-t border-neutral-100 relative overflow-hidden bg-[#fafafa]">
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="flex flex-col items-center gap-8"
        >
          {/* Logo */}
          <div className="flex items-center gap-4">
            <Image
              src="/images/logo.png"
              alt="DO or DICE"
              width={40}
              height={40}
              className="opacity-70"
            />
            <span
              className="text-lg font-semibold text-neutral-600"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              DO or DICE
            </span>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8">
            <a
              href="#features"
              className="text-sm text-neutral-400 hover:text-neutral-900 transition-colors"
            >
              Features
            </a>
            <a
              href="#gameplay"
              className="text-sm text-neutral-400 hover:text-neutral-900 transition-colors"
            >
              How to Play
            </a>
            <a
              href="#rules"
              className="text-sm text-neutral-400 hover:text-neutral-900 transition-colors"
            >
              Rules
            </a>
            <a
              href="https://github.com/Paurakh977/DO-OR-DICE"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-neutral-400 hover:text-neutral-900 transition-colors"
            >
              <Github className="w-4 h-4" />
              Source
            </a>
          </div>

          {/* Divider */}
          <div className="w-24 h-px bg-neutral-200" />

          {/* Copyright */}
          <p className="text-xs text-neutral-400">
            © 2025 DO or DICE. Built with Python & Pygame.
          </p>
        </motion.div>
      </div>
    </footer>
  )
}
